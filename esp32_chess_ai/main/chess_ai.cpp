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

// Comment out ESP_LOG to reduce output
// static const char *TAG = "ChessAI";

// Use USB-Serial/JTAG stdio for input/output
#define STDIN_BUF_SIZE (1024)

// TFLite configuration
constexpr int kTensorArenaSize = 200 * 1024;  // 200KB for ESP32-P4
static uint8_t tensor_arena[kTensorArenaSize];

// Command queue
static QueueHandle_t cmd_queue = NULL;
#define CMD_QUEUE_SIZE 10
#define MAX_CMD_LEN 256

// Piece encoding
typedef enum {
    EMPTY = 0,
    WHITE_PAWN = 1, WHITE_KNIGHT = 2, WHITE_BISHOP = 3,
    WHITE_ROOK = 4, WHITE_QUEEN = 5, WHITE_KING = 6,
    BLACK_PAWN = 7, BLACK_KNIGHT = 8, BLACK_BISHOP = 9,
    BLACK_ROOK = 10, BLACK_QUEEN = 11, BLACK_KING = 12
} Piece;

// Board representation (8x8)
static float board_input[8][8][12];

// Initialize TFLite interpreter
static tflite::MicroInterpreter* interpreter = nullptr;

void init_chess_ai() {
    // ESP_LOGI(TAG, "Initializing Chess AI...");
    printf("Initializing Chess AI...\n");

    // Load model
    const tflite::Model* model = tflite::GetModel(chess_model_tflite);
    if (model->version() != TFLITE_SCHEMA_VERSION) {
        // ESP_LOGE(TAG, "Model version mismatch!");
        printf("Model version mismatch!\n");
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

    // ESP_LOGI(TAG, "Chess AI initialized successfully");
    // ESP_LOGI(TAG, "Tensor arena used: %d / %d bytes",
    //          interpreter->arena_used_bytes(), kTensorArenaSize);
    printf("Chess AI initialized successfully\n");
}

// Convert FEN string to board input tensor
void fen_to_tensor(const char* fen) {
    // Reset board
    memset(board_input, 0, sizeof(board_input));

    int row = 7, col = 0;
    for (int i = 0; fen[i] != ' ' && fen[i] != '\0'; i++) {
        char c = fen[i];
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
            if (piece != EMPTY) {
                board_input[row][col][piece - 1] = 1.0f;
            }
            col++;
        }
    }
}

// Evaluate board position using neural network
float evaluate_position() {
    if (!interpreter) {
        ESP_LOGE(TAG, "Interpreter not initialized");
        return 0.0f;
    }

    // Get input tensor
    TfLiteTensor* input = interpreter->input(0);
    memcpy(input->data.f, board_input, sizeof(board_input));

    // Run inference
    TfLiteStatus invoke_status = interpreter->Invoke();
    if (invoke_status != kTfLiteOk) {
        ESP_LOGE(TAG, "Invoke failed");
        return 0.0f;
    }

    // Get output (evaluation score)
    TfLiteTensor* output = interpreter->output(0);
    float evaluation = *output->data.f;

    return evaluation;
}

// Get best move (simplified - evaluates all legal moves)
const char* get_best_move(const char* fen) {
    // Convert FEN to tensor
    fen_to_tensor(fen);

    // Get base evaluation
    float base_eval = evaluate_position();

    // ESP_LOGI(TAG, "Position evaluation: %.3f", base_eval);
    printf("Position evaluation: %.3f\n", base_eval);

    // TODO: Implement move generation and evaluation
    // This would require a full chess engine with move validation
    // For now, just return the evaluation

    static char result[32];
    snprintf(result, sizeof(result), "eval:%.3f", base_eval);
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
                printf("\r\nAnalyzing position...\r\n");
                const char* result = get_best_move(cmd.fen);
                printf("\r\nResult: %s\r\n", result);
                printf("\r\nNote: Full move generation not implemented yet.\r\n");
                printf("This feature requires move generator and Alpha-Beta search.\r\n");
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
    // Do NOT add this task to watchdog - getchar() blocks
    // esp_task_wdt_add(NULL);

    char cmd_buffer[MAX_CMD_LEN] = {0};
    int cmd_index = 0;

    // ESP_LOGI(TAG, "Stdio task started, waiting for input...");

    while (1) {
        // Read one character from stdin (blocking)
        int c = getchar();

        if (c != EOF) {
            if (c == '\r' || c == '\n') {
                // Command complete
                if (cmd_index > 0) {
                    cmd_buffer[cmd_index] = '\0';
                    printf("\r\n");
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
                printf("%c", c);
                fflush(stdout);
            }
        }
    }
}

// Initialize stdio (USB-Serial/JTAG)
void init_stdio() {
    // USB-Serial/JTAG is already configured by ESP-IDF
    // Just need to enable line buffering for stdin
    setvbuf(stdin, NULL, _IONBF, 0);
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
    printf("Model: chess_ai_model.tflite (170KB)\r\n");
    printf("Input: 8x8x12 board tensor\r\n");
    printf("Output: Position evaluation (-1 to 1)\r\n");
    printf("\r\n");
    printf("Type 'help' for available commands.\r\n");
    printf("\r\n");

    // Create stdio receive task
    xTaskCreate(stdio_rx_task, "stdio_rx_task", 4096, NULL, 5, NULL);

    // Show command prompt
    printf("> ");
    fflush(stdout);

    // Main loop
    while (1) {
        vTaskDelay(pdMS_TO_TICKS(1000));
    }
}