/*
 * Chess AI for ESP32-P4
 * Using TensorFlow Lite Micro for position evaluation
 * Serial command interface for user interaction
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "freertos/queue.h"
#include "esp_log.h"
#include "esp_timer.h"
#include "esp_task_wdt.h"
#include "driver/uart.h"
#include "tensorflow/lite/micro/micro_interpreter.h"
#include "tensorflow/lite/micro/micro_mutable_op_resolver.h"
#include "tensorflow/lite/micro/system_setup.h"
#include "chess_model.h"

static const char *TAG = "ChessAI";

// Use USB-Serial/JTAG stdio for input/output
#define STDIN_BUF_SIZE (1024)

// TFLite configuration
constexpr int kTensorArenaSize = 200 * 1024;  // 200KB for ESP32-P4
static uint8_t tensor_arena[kTensorArenaSize];

// Command configuration
#define MAX_CMD_LEN 256

// Piece encoding
typedef enum {
    EMPTY = 0,
    WHITE_PAWN = 1, WHITE_KNIGHT = 2, WHITE_BISHOP = 3,
    WHITE_ROOK = 4, WHITE_QUEEN = 5, WHITE_KING = 6,
    BLACK_PAWN = 7, BLACK_KNIGHT = 8, BLACK_BISHOP = 9,
    BLACK_ROOK = 10, BLACK_QUEEN = 11, BLACK_KING = 12
} Piece;

// Move structure (UCI format: e2e4, e7e8q for promotion)
typedef struct {
    char from_sq[3];  // e2
    char to_sq[3];    // e4
    char promotion;   // q, r, b, n or 0
} Move;

// Board representation (8x8)
static float board_input[8][8][12];

// Internal board state for move generation
static Piece board[8][8];
static bool is_white_turn = true;
static bool castling_K = true;   // White kingside
static bool castling_Q = true;   // White queenside
static bool castling_k = true;   // Black kingside
static bool castling_q = true;   // Black queenside
static int en_passant_col = -1;  // -1 if no en passant
static int halfmove_clock = 0;
static int fullmove_number = 1;

// Maximum number of legal moves
#define MAX_MOVES 256

// Move generation functions
void init_board_from_fen(const char* fen);
void fen_to_tensor(const char* fen);
float evaluate_position();
int generate_legal_moves(Move* moves);
int generate_pseudo_legal_moves(Move* moves);
bool is_square_attacked(int row, int col, bool by_white);
bool is_in_check(bool white_king);
bool make_move(const Move* move);
void undo_move(const Move* move);
bool is_move_legal(const Move* move);

// Initialize TFLite interpreter
static tflite::MicroInterpreter* interpreter = nullptr;

void init_chess_ai() {
    ESP_LOGI(TAG, "Initializing Chess AI...");

    // Load model
    const tflite::Model* model = tflite::GetModel(chess_model_tflite);
    if (model->version() != TFLITE_SCHEMA_VERSION) {
        ESP_LOGE(TAG, "Model version mismatch!");
        return;
    }

    // Create op resolver
    static tflite::MicroMutableOpResolver<10> resolver;
    resolver.AddConv2D();
    resolver.AddMaxPool2D();
    resolver.AddFullyConnected();
    resolver.AddReshape();
    resolver.AddSoftmax();
    resolver.AddMean();
    resolver.AddMul();
    resolver.AddAdd();
    resolver.AddSub();
    resolver.AddTanh();

    // Create interpreter
    static tflite::MicroInterpreter static_interpreter(
        model, resolver, tensor_arena, kTensorArenaSize);
    interpreter = &static_interpreter;

    // Allocate tensors
    TfLiteStatus allocate_status = interpreter->AllocateTensors();
    if (allocate_status != kTfLiteOk) {
        ESP_LOGE(TAG, "AllocateTensors() failed");
        return;
    }

    ESP_LOGI(TAG, "Chess AI initialized successfully");
    ESP_LOGI(TAG, "Tensor arena used: %d / %d bytes",
             interpreter->arena_used_bytes(), kTensorArenaSize);
}

// Initialize board from FEN string
void init_board_from_fen(const char* fen) {
    // Reset board
    memset(board, 0, sizeof(board));
    castling_K = castling_Q = castling_k = castling_q = false;
    en_passant_col = -1;
    halfmove_clock = 0;
    fullmove_number = 1;

    int row = 7, col = 0;
    int field = 0;  // 0: board, 1: turn, 2: castling, 3: en passant, 4: halfmove, 5: fullmove

    for (int i = 0; fen[i] != '\0'; i++) {
        char c = fen[i];

        if (c == ' ') {
            field++;
            continue;
        }

        switch (field) {
            case 0:  // Board
                if (c == '/') {
                    row--;
                    col = 0;
                } else if (c >= '1' && c <= '8') {
                    col += c - '0';
                } else {
                    Piece piece = EMPTY;
                    switch (c) {
                        case 'P': piece = WHITE_PAWN; break;
                        case 'N': piece = WHITE_KNIGHT; break;
                        case 'B': piece = WHITE_BISHOP; break;
                        case 'R': piece = WHITE_ROOK; break;
                        case 'Q': piece = WHITE_QUEEN; break;
                        case 'K': piece = WHITE_KING; break;
                        case 'p': piece = BLACK_PAWN; break;
                        case 'n': piece = BLACK_KNIGHT; break;
                        case 'b': piece = BLACK_BISHOP; break;
                        case 'r': piece = BLACK_ROOK; break;
                        case 'q': piece = BLACK_QUEEN; break;
                        case 'k': piece = BLACK_KING; break;
                    }
                    if (row >= 0 && row < 8 && col >= 0 && col < 8) {
                        board[row][col] = piece;
                    }
                    col++;
                }
                break;

            case 1:  // Turn
                is_white_turn = (c == 'w');
                break;

            case 2:  // Castling
                if (c == 'K') castling_K = true;
                else if (c == 'Q') castling_Q = true;
                else if (c == 'k') castling_k = true;
                else if (c == 'q') castling_q = true;
                break;

            case 3:  // En passant
                if (c != '-') {
                    en_passant_col = c - 'a';
                }
                break;

            case 4:  // Halfmove clock
                if (c >= '0' && c <= '9') {
                    halfmove_clock = halfmove_clock * 10 + (c - '0');
                }
                break;

            case 5:  // Fullmove number
                if (c >= '0' && c <= '9') {
                    fullmove_number = fullmove_number * 10 + (c - '0');
                }
                break;
        }
    }
}

// Convert FEN string to board input tensor
void fen_to_tensor(const char* fen) {
    // Initialize internal board
    init_board_from_fen(fen);

    // Reset tensor
    memset(board_input, 0, sizeof(board_input));

    // Convert board to tensor
    for (int row = 0; row < 8; row++) {
        for (int col = 0; col < 8; col++) {
            Piece piece = board[row][col];
            if (piece != EMPTY) {
                board_input[row][col][piece - 1] = 1.0f;
            }
        }
    }
}

// Check if a square is attacked by any piece
bool is_square_attacked(int row, int col, bool by_white) {
    // Check pawn attacks
    int pawn_dir = by_white ? -1 : 1;
    if (row + pawn_dir >= 0 && row + pawn_dir < 8) {
        if (col - 1 >= 0) {
            Piece p = board[row + pawn_dir][col - 1];
            if (by_white && p == WHITE_PAWN) return true;
            if (!by_white && p == BLACK_PAWN) return true;
        }
        if (col + 1 < 8) {
            Piece p = board[row + pawn_dir][col + 1];
            if (by_white && p == WHITE_PAWN) return true;
            if (!by_white && p == BLACK_PAWN) return true;
        }
    }

    // Check knight attacks
    int knight_moves[8][2] = {{-2,-1}, {-2,1}, {-1,-2}, {-1,2}, {1,-2}, {1,2}, {2,-1}, {2,1}};
    for (int i = 0; i < 8; i++) {
        int r = row + knight_moves[i][0];
        int c = col + knight_moves[i][1];
        if (r >= 0 && r < 8 && c >= 0 && c < 8) {
            Piece p = board[r][c];
            if (by_white && p == WHITE_KNIGHT) return true;
            if (!by_white && p == BLACK_KNIGHT) return true;
        }
    }

    // Check king attacks
    for (int dr = -1; dr <= 1; dr++) {
        for (int dc = -1; dc <= 1; dc++) {
            if (dr == 0 && dc == 0) continue;
            int r = row + dr;
            int c = col + dc;
            if (r >= 0 && r < 8 && c >= 0 && c < 8) {
                Piece p = board[r][c];
                if (by_white && p == WHITE_KING) return true;
                if (!by_white && p == BLACK_KING) return true;
            }
        }
    }

    // Check sliding piece attacks (bishop, rook, queen)
    int directions[8][2] = {{-1,0}, {1,0}, {0,-1}, {0,1}, {-1,-1}, {-1,1}, {1,-1}, {1,1}};
    for (int i = 0; i < 8; i++) {
        int dr = directions[i][0];
        int dc = directions[i][1];
        int r = row + dr;
        int c = col + dc;

        while (r >= 0 && r < 8 && c >= 0 && c < 8) {
            Piece p = board[r][c];
            if (p != EMPTY) {
                // Check if this piece can attack
                bool is_diag = (dr != 0 && dc != 0);
                bool is_orth = (dr == 0 || dc == 0);

                if (by_white) {
                    if (is_diag && (p == WHITE_BISHOP || p == WHITE_QUEEN)) return true;
                    if (is_orth && (p == WHITE_ROOK || p == WHITE_QUEEN)) return true;
                } else {
                    if (is_diag && (p == BLACK_BISHOP || p == BLACK_QUEEN)) return true;
                    if (is_orth && (p == BLACK_ROOK || p == BLACK_QUEEN)) return true;
                }
                break;
            }
            r += dr;
            c += dc;
        }
    }

    return false;
}

// Check if king is in check
bool is_in_check(bool white_king) {
    // Find king position
    int king_row = -1, king_col = -1;
    Piece king_piece = white_king ? WHITE_KING : BLACK_KING;

    for (int r = 0; r < 8; r++) {
        for (int c = 0; c < 8; c++) {
            if (board[r][c] == king_piece) {
                king_row = r;
                king_col = c;
                break;
            }
        }
        if (king_row != -1) break;
    }

    if (king_row == -1) return false;  // King not found (shouldn't happen)

    return is_square_attacked(king_row, king_col, !white_king);
}

// Evaluate board position using neural network
float evaluate_position() {
    if (!interpreter) {
        ESP_LOGE(TAG, "Interpreter not initialized");
        return 0.0f;
    }

    // Feed watchdog before inference
    esp_task_wdt_reset();

    // Get input tensor
    TfLiteTensor* input = interpreter->input(0);
    memcpy(input->data.f, board_input, sizeof(board_input));

    // Run inference
    TfLiteStatus invoke_status = interpreter->Invoke();
    if (invoke_status != kTfLiteOk) {
        ESP_LOGE(TAG, "Invoke failed");
        return 0.0f;
    }

    // Feed watchdog after inference
    esp_task_wdt_reset();

    // Get output (evaluation score)
    TfLiteTensor* output = interpreter->output(0);
    float evaluation = *output->data.f;

    return evaluation;
}

// Generate pseudo-legal moves (doesn't check for king safety)
int generate_pseudo_legal_moves(Move* moves) {
    int count = 0;
    bool white = is_white_turn;

    // Debug: print board state
    ESP_LOGI(TAG, "Generating moves for %s", white ? "white" : "black");
    for (int r = 0; r < 8; r++) {
        char row_str[9];
        for (int c = 0; c < 8; c++) {
            Piece p = board[r][c];
            char ch = '.';
            if (p != EMPTY) {
                switch(p) {
                    case EMPTY: ch = '.'; break;
                    case WHITE_PAWN: ch = 'P'; break;
                    case WHITE_KNIGHT: ch = 'N'; break;
                    case WHITE_BISHOP: ch = 'B'; break;
                    case WHITE_ROOK: ch = 'R'; break;
                    case WHITE_QUEEN: ch = 'Q'; break;
                    case WHITE_KING: ch = 'K'; break;
                    case BLACK_PAWN: ch = 'p'; break;
                    case BLACK_KNIGHT: ch = 'n'; break;
                    case BLACK_BISHOP: ch = 'b'; break;
                    case BLACK_ROOK: ch = 'r'; break;
                    case BLACK_QUEEN: ch = 'q'; break;
                    case BLACK_KING: ch = 'k'; break;
                }
            }
            row_str[c] = ch;
        }
        row_str[8] = '\0';
        ESP_LOGI(TAG, "Row %d: %s", r+1, row_str);
    }

    for (int row = 0; row < 8; row++) {
        for (int col = 0; col < 8; col++) {
            Piece piece = board[row][col];

            // Skip empty squares and opponent pieces
            if (piece == EMPTY) continue;
            if (white && piece > WHITE_KING) {
                ESP_LOGI(TAG, "Skipping black piece at %c%d: piece=%d", 'a'+col, row+1, piece);
                continue;
            }
            if (!white && piece <= WHITE_KING) {
                ESP_LOGI(TAG, "Skipping white piece at %c%d: piece=%d", 'a'+col, row+1, piece);
                continue;
            }
            ESP_LOGI(TAG, "Processing %s piece at %c%d: piece=%d", white ? "white" : "black", 'a'+col, row+1, piece);

            // Generate moves based on piece type
            switch (piece) {
                case WHITE_PAWN:
                case BLACK_PAWN: {
                    int dir = white ? 1 : -1;
                    int start_row = white ? 1 : 6;

                    // Forward move
                    if (row + dir >= 0 && row + dir < 8 && board[row + dir][col] == EMPTY) {
                        moves[count].from_sq[0] = 'a' + col;
                        moves[count].from_sq[1] = '1' + row;
                        moves[count].from_sq[2] = '\0';
                        moves[count].to_sq[0] = 'a' + col;
                        moves[count].to_sq[1] = '1' + row + dir;
                        moves[count].to_sq[2] = '\0';
                        moves[count].promotion = 0;

                        // Check for promotion
                        if ((white && row + dir == 0) || (!white && row + dir == 7)) {
                            moves[count].promotion = 'q';  // Default to queen
                            count++;
                            moves[count] = moves[count - 1];
                            moves[count].promotion = 'r';
                            count++;
                            moves[count] = moves[count - 1];
                            moves[count].promotion = 'b';
                            count++;
                            moves[count] = moves[count - 1];
                            moves[count].promotion = 'n';
                            count++;
                        } else {
                            count++;
                        }

                        // Double pawn move from starting position
                        if (row == start_row && board[row + 2 * dir][col] == EMPTY) {
                            moves[count].from_sq[0] = 'a' + col;
                            moves[count].from_sq[1] = '1' + row;
                            moves[count].from_sq[2] = '\0';
                            moves[count].to_sq[0] = 'a' + col;
                            moves[count].to_sq[1] = '1' + row + 2 * dir;
                            moves[count].to_sq[2] = '\0';
                            moves[count].promotion = 0;
                            count++;
                        }
                    }

                    // Captures
                    for (int dc = -1; dc <= 1; dc += 2) {
                        int new_col = col + dc;
                        if (new_col >= 0 && new_col < 8 && row + dir >= 0 && row + dir < 8) {
                            Piece target = board[row + dir][new_col];
                            bool capture = (target != EMPTY);
                            bool en_passant = (new_col == en_passant_col && row + dir == (white ? 2 : 5));

                            if (capture || en_passant) {
                                bool valid_capture = false;
                                if (white && target > WHITE_KING) valid_capture = true;
                                if (!white && target <= WHITE_KING && target != EMPTY) valid_capture = true;

                                if (valid_capture || en_passant) {
                                    moves[count].from_sq[0] = 'a' + col;
                                    moves[count].from_sq[1] = '1' + row;
                                    moves[count].from_sq[2] = '\0';
                                    moves[count].to_sq[0] = 'a' + new_col;
                                    moves[count].to_sq[1] = '1' + row + dir;
                                    moves[count].to_sq[2] = '\0';

                                    // Check for promotion
                                    if ((white && row + dir == 0) || (!white && row + dir == 7)) {
                                        moves[count].promotion = 'q';
                                        count++;
                                        moves[count] = moves[count - 1];
                                        moves[count].promotion = 'r';
                                        count++;
                                        moves[count] = moves[count - 1];
                                        moves[count].promotion = 'b';
                                        count++;
                                        moves[count] = moves[count - 1];
                                        moves[count].promotion = 'n';
                                        count++;
                                    } else {
                                        moves[count].promotion = 0;
                                        count++;
                                    }
                                }
                            }
                        }
                    }
                    break;
                }

                case WHITE_KNIGHT:
                case BLACK_KNIGHT: {
                    int knight_moves[8][2] = {{-2,-1}, {-2,1}, {-1,-2}, {-1,2}, {1,-2}, {1,2}, {2,-1}, {2,1}};
                    for (int i = 0; i < 8; i++) {
                        int new_row = row + knight_moves[i][0];
                        int new_col = col + knight_moves[i][1];
                        if (new_row >= 0 && new_row < 8 && new_col >= 0 && new_col < 8) {
                            Piece target = board[new_row][new_col];
                            if (target == EMPTY) {
                                // Empty square
                            } else if (white && target > WHITE_KING) {
                                // Capture black piece
                            } else if (!white && target <= WHITE_KING) {
                                // Capture white piece
                            } else {
                                continue;  // Can't capture own piece
                            }
                            moves[count].from_sq[0] = 'a' + col;
                            moves[count].from_sq[1] = '1' + row;
                            moves[count].from_sq[2] = '\0';
                            moves[count].to_sq[0] = 'a' + new_col;
                            moves[count].to_sq[1] = '1' + new_row;
                            moves[count].to_sq[2] = '\0';
                            moves[count].promotion = 0;
                            count++;
                        }
                    }
                    break;
                }

                case WHITE_BISHOP:
                case BLACK_BISHOP: {
                    int directions[4][2] = {{-1,-1}, {-1,1}, {1,-1}, {1,1}};
                    for (int i = 0; i < 4; i++) {
                        int dr = directions[i][0];
                        int dc = directions[i][1];
                        int new_row = row + dr;
                        int new_col = col + dc;
                        while (new_row >= 0 && new_row < 8 && new_col >= 0 && new_col < 8) {
                            Piece target = board[new_row][new_col];
                            if (target == EMPTY) {
                                moves[count].from_sq[0] = 'a' + col;
                                moves[count].from_sq[1] = '1' + row;
                                moves[count].from_sq[2] = '\0';
                                moves[count].to_sq[0] = 'a' + new_col;
                                moves[count].to_sq[1] = '1' + new_row;
                                moves[count].to_sq[2] = '\0';
                                moves[count].promotion = 0;
                                count++;
                            } else {
                                if (white && target > WHITE_KING) {
                                    // Capture black piece
                                    moves[count].from_sq[0] = 'a' + col;
                                    moves[count].from_sq[1] = '1' + row;
                                    moves[count].from_sq[2] = '\0';
                                    moves[count].to_sq[0] = 'a' + new_col;
                                    moves[count].to_sq[1] = '1' + new_row;
                                    moves[count].to_sq[2] = '\0';
                                    moves[count].promotion = 0;
                                    count++;
                                } else if (!white && target <= WHITE_KING) {
                                    // Capture white piece
                                    moves[count].from_sq[0] = 'a' + col;
                                    moves[count].from_sq[1] = '1' + row;
                                    moves[count].from_sq[2] = '\0';
                                    moves[count].to_sq[0] = 'a' + new_col;
                                    moves[count].to_sq[1] = '1' + new_row;
                                    moves[count].to_sq[2] = '\0';
                                    moves[count].promotion = 0;
                                    count++;
                                }
                                break;  // Stop at first piece
                            }
                            new_row += dr;
                            new_col += dc;
                        }
                    }
                    break;
                }

                case WHITE_ROOK:
                case BLACK_ROOK: {
                    int directions[4][2] = {{-1,0}, {1,0}, {0,-1}, {0,1}};
                    for (int i = 0; i < 4; i++) {
                        int dr = directions[i][0];
                        int dc = directions[i][1];
                        int new_row = row + dr;
                        int new_col = col + dc;
                        while (new_row >= 0 && new_row < 8 && new_col >= 0 && new_col < 8) {
                            Piece target = board[new_row][new_col];
                            if (target == EMPTY) {
                                moves[count].from_sq[0] = 'a' + col;
                                moves[count].from_sq[1] = '1' + row;
                                moves[count].from_sq[2] = '\0';
                                moves[count].to_sq[0] = 'a' + new_col;
                                moves[count].to_sq[1] = '1' + new_row;
                                moves[count].to_sq[2] = '\0';
                                moves[count].promotion = 0;
                                count++;
                            } else {
                                if (white && target > WHITE_KING) {
                                    moves[count].from_sq[0] = 'a' + col;
                                    moves[count].from_sq[1] = '1' + row;
                                    moves[count].from_sq[2] = '\0';
                                    moves[count].to_sq[0] = 'a' + new_col;
                                    moves[count].to_sq[1] = '1' + new_row;
                                    moves[count].to_sq[2] = '\0';
                                    moves[count].promotion = 0;
                                    count++;
                                } else if (!white && target <= WHITE_KING) {
                                    moves[count].from_sq[0] = 'a' + col;
                                    moves[count].from_sq[1] = '1' + row;
                                    moves[count].from_sq[2] = '\0';
                                    moves[count].to_sq[0] = 'a' + new_col;
                                    moves[count].to_sq[1] = '1' + new_row;
                                    moves[count].to_sq[2] = '\0';
                                    moves[count].promotion = 0;
                                    count++;
                                }
                                break;
                            }
                            new_row += dr;
                            new_col += dc;
                        }
                    }
                    break;
                }

                case WHITE_QUEEN:
                case BLACK_QUEEN: {
                    int directions[8][2] = {{-1,0}, {1,0}, {0,-1}, {0,1}, {-1,-1}, {-1,1}, {1,-1}, {1,1}};
                    for (int i = 0; i < 8; i++) {
                        int dr = directions[i][0];
                        int dc = directions[i][1];
                        int new_row = row + dr;
                        int new_col = col + dc;
                        while (new_row >= 0 && new_row < 8 && new_col >= 0 && new_col < 8) {
                            Piece target = board[new_row][new_col];
                            if (target == EMPTY) {
                                moves[count].from_sq[0] = 'a' + col;
                                moves[count].from_sq[1] = '1' + row;
                                moves[count].from_sq[2] = '\0';
                                moves[count].to_sq[0] = 'a' + new_col;
                                moves[count].to_sq[1] = '1' + new_row;
                                moves[count].to_sq[2] = '\0';
                                moves[count].promotion = 0;
                                count++;
                            } else {
                                if (white && target > WHITE_KING) {
                                    moves[count].from_sq[0] = 'a' + col;
                                    moves[count].from_sq[1] = '1' + row;
                                    moves[count].from_sq[2] = '\0';
                                    moves[count].to_sq[0] = 'a' + new_col;
                                    moves[count].to_sq[1] = '1' + new_row;
                                    moves[count].to_sq[2] = '\0';
                                    moves[count].promotion = 0;
                                    count++;
                                } else if (!white && target <= WHITE_KING) {
                                    moves[count].from_sq[0] = 'a' + col;
                                    moves[count].from_sq[1] = '1' + row;
                                    moves[count].from_sq[2] = '\0';
                                    moves[count].to_sq[0] = 'a' + new_col;
                                    moves[count].to_sq[1] = '1' + new_row;
                                    moves[count].to_sq[2] = '\0';
                                    moves[count].promotion = 0;
                                    count++;
                                }
                                break;
                            }
                            new_row += dr;
                            new_col += dc;
                        }
                    }
                    break;
                }

                case WHITE_KING:
                case BLACK_KING: {
                    for (int dr = -1; dr <= 1; dr++) {
                        for (int dc = -1; dc <= 1; dc++) {
                            if (dr == 0 && dc == 0) continue;
                            int new_row = row + dr;
                            int new_col = col + dc;
                            if (new_row >= 0 && new_row < 8 && new_col >= 0 && new_col < 8) {
                                Piece target = board[new_row][new_col];
                                if (target == EMPTY) {
                                    moves[count].from_sq[0] = 'a' + col;
                                    moves[count].from_sq[1] = '1' + row;
                                    moves[count].from_sq[2] = '\0';
                                    moves[count].to_sq[0] = 'a' + new_col;
                                    moves[count].to_sq[1] = '1' + new_row;
                                    moves[count].to_sq[2] = '\0';
                                    moves[count].promotion = 0;
                                    count++;
                                } else if (white && target > WHITE_KING) {
                                    moves[count].from_sq[0] = 'a' + col;
                                    moves[count].from_sq[1] = '1' + row;
                                    moves[count].from_sq[2] = '\0';
                                    moves[count].to_sq[0] = 'a' + new_col;
                                    moves[count].to_sq[1] = '1' + new_row;
                                    moves[count].to_sq[2] = '\0';
                                    moves[count].promotion = 0;
                                    count++;
                                } else if (!white && target <= WHITE_KING) {
                                    moves[count].from_sq[0] = 'a' + col;
                                    moves[count].from_sq[1] = '1' + row;
                                    moves[count].from_sq[2] = '\0';
                                    moves[count].to_sq[0] = 'a' + new_col;
                                    moves[count].to_sq[1] = '1' + new_row;
                                    moves[count].to_sq[2] = '\0';
                                    moves[count].promotion = 0;
                                    count++;
                                }
                            }
                        }
                    }

                    // Castling
                    if (white) {
                        // Kingside castling
                        if (castling_K && board[7][5] == EMPTY && board[7][6] == EMPTY &&
                            !is_square_attacked(7, 4, false) &&
                            !is_square_attacked(7, 5, false) &&
                            !is_square_attacked(7, 6, false)) {
                            moves[count].from_sq[0] = 'e';
                            moves[count].from_sq[1] = '1';
                            moves[count].from_sq[2] = '\0';
                            moves[count].to_sq[0] = 'g';
                            moves[count].to_sq[1] = '1';
                            moves[count].to_sq[2] = '\0';
                            moves[count].promotion = 0;
                            count++;
                        }
                        // Queenside castling
                        if (castling_Q && board[7][1] == EMPTY && board[7][2] == EMPTY && board[7][3] == EMPTY &&
                            !is_square_attacked(7, 4, false) &&
                            !is_square_attacked(7, 3, false) &&
                            !is_square_attacked(7, 2, false)) {
                            moves[count].from_sq[0] = 'e';
                            moves[count].from_sq[1] = '1';
                            moves[count].from_sq[2] = '\0';
                            moves[count].to_sq[0] = 'c';
                            moves[count].to_sq[1] = '1';
                            moves[count].to_sq[2] = '\0';
                            moves[count].promotion = 0;
                            count++;
                        }
                    } else {
                        // Kingside castling
                        if (castling_k && board[0][5] == EMPTY && board[0][6] == EMPTY &&
                            !is_square_attacked(0, 4, true) &&
                            !is_square_attacked(0, 5, true) &&
                            !is_square_attacked(0, 6, true)) {
                            moves[count].from_sq[0] = 'e';
                            moves[count].from_sq[1] = '8';
                            moves[count].from_sq[2] = '\0';
                            moves[count].to_sq[0] = 'g';
                            moves[count].to_sq[1] = '8';
                            moves[count].to_sq[2] = '\0';
                            moves[count].promotion = 0;
                            count++;
                        }
                        // Queenside castling
                        if (castling_q && board[0][1] == EMPTY && board[0][2] == EMPTY && board[0][3] == EMPTY &&
                            !is_square_attacked(0, 4, true) &&
                            !is_square_attacked(0, 3, true) &&
                            !is_square_attacked(0, 2, true)) {
                            moves[count].from_sq[0] = 'e';
                            moves[count].from_sq[1] = '8';
                            moves[count].from_sq[2] = '\0';
                            moves[count].to_sq[0] = 'c';
                            moves[count].to_sq[1] = '8';
                            moves[count].to_sq[2] = '\0';
                            moves[count].promotion = 0;
                            count++;
                        }
                    }
                    break;
                }

                default:
                    break;
            }
        }
    }

    return count;
}

// Generate legal moves (checks for king safety)
int generate_legal_moves(Move* moves) {
    Move pseudo_moves[MAX_MOVES];
    int pseudo_count = generate_pseudo_legal_moves(pseudo_moves);
    int legal_count = 0;

    for (int i = 0; i < pseudo_count; i++) {
        if (is_move_legal(&pseudo_moves[i])) {
            moves[legal_count++] = pseudo_moves[i];
        }
    }

    return legal_count;
}

// Check if a move is legal (doesn't leave king in check)
bool is_move_legal(const Move* move) {
    // Save current state
    Piece saved_board[8][8];
    memcpy(saved_board, board, sizeof(board));
    bool saved_white_turn = is_white_turn;
    bool saved_castling_K = castling_K;
    bool saved_castling_Q = castling_Q;
    bool saved_castling_k = castling_k;
    bool saved_castling_q = castling_q;
    int saved_en_passant_col = en_passant_col;

    // Make the move
    if (!make_move(move)) {
        return false;
    }

    // Check if king is in check
    bool in_check = is_in_check(saved_white_turn);

    // Restore state
    memcpy(board, saved_board, sizeof(board));
    is_white_turn = saved_white_turn;
    castling_K = saved_castling_K;
    castling_Q = saved_castling_Q;
    castling_k = saved_castling_k;
    castling_q = saved_castling_q;
    en_passant_col = saved_en_passant_col;

    return !in_check;
}

// Make a move on the board
bool make_move(const Move* move) {
    int from_row = move->from_sq[1] - '1';
    int from_col = move->from_sq[0] - 'a';
    int to_row = move->to_sq[1] - '1';
    int to_col = move->to_sq[0] - 'a';

    if (from_row < 0 || from_row >= 8 || from_col < 0 || from_col >= 8 ||
        to_row < 0 || to_row >= 8 || to_col < 0 || to_col >= 8) {
        return false;
    }

    Piece piece = board[from_row][from_col];
    if (piece == EMPTY) return false;

    // Check if it's the right color's turn
    bool white_piece = (piece <= WHITE_KING);
    if (white_piece != is_white_turn) return false;

    // Handle castling
    if ((piece == WHITE_KING || piece == BLACK_KING) &&
        abs(from_col - to_col) == 2) {
        // Kingside castling
        if (to_col > from_col) {
            board[from_row][5] = board[from_row][7];
            board[from_row][7] = EMPTY;
        }
        // Queenside castling
        else {
            board[from_row][3] = board[from_row][0];
            board[from_row][0] = EMPTY;
        }
    }

    // Handle en passant capture
    if ((piece == WHITE_PAWN || piece == BLACK_PAWN) &&
        to_col != from_col && board[to_row][to_col] == EMPTY) {
        int capture_row = is_white_turn ? to_row + 1 : to_row - 1;
        board[capture_row][to_col] = EMPTY;
    }

    // Move the piece
    board[to_row][to_col] = piece;
    board[from_row][from_col] = EMPTY;

    // Handle promotion
    if (move->promotion != 0) {
        switch (move->promotion) {
            case 'q':
                board[to_row][to_col] = is_white_turn ? WHITE_QUEEN : BLACK_QUEEN;
                break;
            case 'r':
                board[to_row][to_col] = is_white_turn ? WHITE_ROOK : BLACK_ROOK;
                break;
            case 'b':
                board[to_row][to_col] = is_white_turn ? WHITE_BISHOP : BLACK_BISHOP;
                break;
            case 'n':
                board[to_row][to_col] = is_white_turn ? WHITE_KNIGHT : BLACK_KNIGHT;
                break;
        }
    }

    // Update castling rights
    if (piece == WHITE_KING) {
        castling_K = false;
        castling_Q = false;
    } else if (piece == BLACK_KING) {
        castling_k = false;
        castling_q = false;
    } else if (piece == WHITE_ROOK) {
        if (from_row == 7 && from_col == 0) castling_Q = false;
        if (from_row == 7 && from_col == 7) castling_K = false;
    } else if (piece == BLACK_ROOK) {
        if (from_row == 0 && from_col == 0) castling_q = false;
        if (from_row == 0 && from_col == 7) castling_k = false;
    }

    // Update en passant square
    en_passant_col = -1;
    if ((piece == WHITE_PAWN || piece == BLACK_PAWN) && abs(from_row - to_row) == 2) {
        en_passant_col = from_col;
    }

    // Switch turn
    is_white_turn = !is_white_turn;

    return true;
}

// Undo a move (simplified - doesn't restore all state)
void undo_move(const Move* move) {
    // For now, just switch turn back
    // Full implementation would need to save more state
    is_white_turn = !is_white_turn;
}

// Get best move (evaluates all legal moves)
const char* get_best_move(const char* fen) {
    // Convert FEN to tensor
    fen_to_tensor(fen);

    // Get base evaluation
    float base_eval = evaluate_position();

    ESP_LOGI(TAG, "Position evaluation: %.3f", base_eval);

    // Generate all legal moves
    Move moves[MAX_MOVES];
    int move_count = generate_legal_moves(moves);

    ESP_LOGI(TAG, "Generated %d legal moves", move_count);

    if (move_count == 0) {
        static char result[32];
        if (is_in_check(is_white_turn)) {
            snprintf(result, sizeof(result), "checkmate");
        } else {
            snprintf(result, sizeof(result), "stalemate");
        }
        return result;
    }

    // Evaluate each move
    float best_eval = -2.0f;
    int best_move_idx = 0;

    for (int i = 0; i < move_count; i++) {
        // Reset watchdog before processing each move
        esp_task_wdt_reset();

        // Save current board state
        Piece saved_board[8][8];
        memcpy(saved_board, board, sizeof(board));
        bool saved_white_turn = is_white_turn;
        bool saved_castling_K = castling_K;
        bool saved_castling_Q = castling_Q;
        bool saved_castling_k = castling_k;
        bool saved_castling_q = castling_q;
        int saved_en_passant_col = en_passant_col;

        // Make the move
        if (make_move(&moves[i])) {
            // Reset watchdog before evaluation
            esp_task_wdt_reset();

            // Evaluate the resulting position
            fen_to_tensor(fen);  // Re-initialize from saved state
            init_board_from_fen(fen);  // This is a workaround - should use saved state
            make_move(&moves[i]);  // Make the move again

            float eval = evaluate_position();

            // Reset watchdog after evaluation
            esp_task_wdt_reset();

            // For white, we want to maximize; for black, minimize
            if (is_white_turn) {
                eval = -eval;  // After making a move, it's black's turn
            }

            ESP_LOGI(TAG, "Move %s%s: eval=%.3f", moves[i].from_sq, moves[i].to_sq, eval);

            if (eval > best_eval) {
                best_eval = eval;
                best_move_idx = i;
            }
        }

        // Restore board state
        memcpy(board, saved_board, sizeof(board));
        is_white_turn = saved_white_turn;
        castling_K = saved_castling_K;
        castling_Q = saved_castling_Q;
        castling_k = saved_castling_k;
        castling_q = saved_castling_q;
        en_passant_col = saved_en_passant_col;

        // Reset watchdog after restoring state
        esp_task_wdt_reset();
    }

    // Format the best move
    static char result[16];
    if (moves[best_move_idx].promotion != 0) {
        snprintf(result, sizeof(result), "%s%s%c",
                 moves[best_move_idx].from_sq,
                 moves[best_move_idx].to_sq,
                 moves[best_move_idx].promotion);
    } else {
        snprintf(result, sizeof(result), "%s%s",
                 moves[best_move_idx].from_sq,
                 moves[best_move_idx].to_sq);
    }

    ESP_LOGI(TAG, "Best move: %s (eval=%.3f)", result, best_eval);

    return result;
}

// Command types
typedef enum {
    CMD_EVAL,
    CMD_BESTMOVE,
    CMD_HELP,
    CMD_UNKNOWN
} CommandType;

// Command structure
typedef struct {
    CommandType type;
    char fen[128];
} Command;

// Parse command from string
Command parse_command(const char* cmd_str) {
    Command cmd = {CMD_UNKNOWN, ""};

    char cmd_copy[MAX_CMD_LEN];
    strncpy(cmd_copy, cmd_str, MAX_CMD_LEN - 1);
    cmd_copy[MAX_CMD_LEN - 1] = '\0';

    // Trim whitespace
    char* token = strtok(cmd_copy, " \t\n\r");

    if (token == NULL) {
        return cmd;
    }

    if (strcmp(token, "eval") == 0) {
        cmd.type = CMD_EVAL;
        token = strtok(NULL, "");
        if (token) {
            // Trim leading whitespace
            while (*token == ' ') token++;
            strncpy(cmd.fen, token, sizeof(cmd.fen) - 1);
        }
    } else if (strcmp(token, "bestmove") == 0) {
        cmd.type = CMD_BESTMOVE;
        token = strtok(NULL, "");
        if (token) {
            while (*token == ' ') token++;
            strncpy(cmd.fen, token, sizeof(cmd.fen) - 1);
        }
    } else if (strcmp(token, "help") == 0 || strcmp(token, "?") == 0) {
        cmd.type = CMD_HELP;
    }

    return cmd;
}

// Execute command
void execute_command(Command cmd) {
    switch (cmd.type) {
        case CMD_EVAL:
            if (strlen(cmd.fen) > 0) {
                int64_t start_time = esp_timer_get_time();
                fen_to_tensor(cmd.fen);
                float eval = evaluate_position();
                int64_t end_time = esp_timer_get_time();
                float time_ms = (end_time - start_time) / 1000.0f;

                printf("\r\nEvaluation: %.3f", eval);
                if (eval > 0.3) printf(" (白方优势)");
                else if (eval < -0.3) printf(" (黑方优势)");
                else printf(" (均势)");
                printf("\r\nTime: %.2f ms\r\n", time_ms);
            } else {
                printf("\r\nError: Missing FEN string\r\n");
                printf("Usage: eval <fen>\r\n");
            }
            break;

        case CMD_BESTMOVE:
            if (strlen(cmd.fen) > 0) {
                int64_t start_time = esp_timer_get_time();
                printf("\r\nAnalyzing position...\r\n");
                const char* result = get_best_move(cmd.fen);
                int64_t end_time = esp_timer_get_time();
                float time_ms = (end_time - start_time) / 1000.0f;

                printf("\r\nBest move: %s\r\n", result);
                printf("Time: %.2f ms\r\n", time_ms);
                printf("Depth: 1 (single-ply search)\r\n");
                printf("Note: For better play, use Stockfish or implement Alpha-Beta search.\r\n");
            } else {
                printf("\r\nError: Missing FEN string\r\n");
                printf("Usage: bestmove <fen>\r\n");
            }
            break;

        case CMD_HELP:
            printf("\r\n");
            printf("========================================\r\n");
            printf("        ESP32-P4 Chess AI Commands\r\n");
            printf("========================================\r\n");
            printf("\r\n");
            printf("eval <fen>       - Evaluate a chess position\r\n");
            printf("                  Example: eval rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1\r\n");
            printf("\r\n");
            printf("bestmove <fen>   - Get the best move for a position\r\n");
            printf("                  Example: bestmove rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1\r\n");
            printf("\r\n");
            printf("help             - Show this help message\r\n");
            printf("?                - Show this help message\r\n");
            printf("\r\n");
            printf("========================================\r\n");
            printf("\r\n");
            break;

        case CMD_UNKNOWN:
            printf("\r\nUnknown command. Type 'help' for available commands.\r\n");
            break;
    }

    printf("\r\n> ");
    fflush(stdout);
}

// UART receive task
static void stdio_rx_task(void *pvParameters) {
    // Initialize stdin
    char cmd_buffer[MAX_CMD_LEN] = {0};
    int cmd_index = 0;

    ESP_LOGI(TAG, "Stdio task started, waiting for input...");

    while (1) {
        // Feed watchdog to prevent timeout
        esp_task_wdt_reset();

        // Check if there's data available (non-blocking)
        int c = getchar();

        if (c != EOF) {
            if (c == '\r' || c == '\n') {
                // Command complete
                if (cmd_index > 0) {
                    cmd_buffer[cmd_index] = '\0';
                    printf("\r\n");
                    fflush(stdout);
                    Command cmd = parse_command(cmd_buffer);
                    execute_command(cmd);
                    cmd_index = 0;
                }
            } else if (c == 8 || c == 127) {
                // Backspace
                if (cmd_index > 0) {
                    cmd_index--;
                    printf("\b \b");
                    fflush(stdout);
                }
            } else if (cmd_index < MAX_CMD_LEN - 1) {
                // Regular character
                cmd_buffer[cmd_index++] = (char)c;
                putchar(c);  // Use putchar for immediate output
                fflush(stdout);  // Force flush
            }
        } else {
            // No data available, yield CPU for 5ms (faster polling)
            vTaskDelay(pdMS_TO_TICKS(5));
        }
    }
}

// Initialize stdio (USB-Serial/JTAG)
void init_stdio() {
    // USB-Serial/JTAG is already configured by ESP-IDF
    // Disable buffering for stdin and stdout
    setvbuf(stdin, NULL, _IONBF, 0);
    setvbuf(stdout, NULL, _IONBF, 0);

    // Ensure line buffering is disabled for immediate output
    setlinebuf(stdout);

    ESP_LOGI(TAG, "Stdio initialized (USB-Serial/JTAG)");
}

extern "C" void app_main(void) {
    ESP_LOGI(TAG, "Chess AI starting...");

    // Initialize stdio (USB-Serial/JTAG)
    init_stdio();

    // Initialize AI
    init_chess_ai();

    // Print welcome message
    printf("\r\n");
    printf("****************************************\r\n");
    printf("*      ESP32-P4 Chess AI v1.0         *\r\n");
    printf("*      Neural Network Evaluator       *\r\n");
    printf("****************************************\r\n");
    printf("\r\n");
    printf("Model: chess_ai_model.tflite (639KB)\r\n");
    printf("Input: 8x8x12 board tensor\r\n");
    printf("Output: Position evaluation (-1 to 1)\r\n");
    printf("\r\n");
    printf("Type 'help' for available commands.\r\n");
    printf("\r\n");

    // Initialize task watchdog
    // Use default configuration (5 seconds timeout)
    esp_task_wdt_config_t twdt_config = {
        .timeout_ms = 5000,
        .idle_core_mask = 0,  // Don't trigger on idle tasks
        .trigger_panic = false  // Don't panic on timeout, just print warning
    };
    esp_task_wdt_init(&twdt_config);

    // Create stdio receive task
    TaskHandle_t stdio_task_handle = NULL;
    xTaskCreate(stdio_rx_task, "stdio_rx_task", 32768, NULL, 5, &stdio_task_handle);

    // Add task to watchdog
    if (stdio_task_handle != NULL) {
        esp_task_wdt_add(stdio_task_handle);
    }

    // Show command prompt
    printf("> ");
    fflush(stdout);

    // Main loop
    while (1) {
        vTaskDelay(pdMS_TO_TICKS(1000));
    }
}
