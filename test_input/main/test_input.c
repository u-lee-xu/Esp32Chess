/*
 * Simple test program for USB-Serial/JTAG input
 * This program waits for user input and echoes it back
 */

#include <stdio.h>
#include <string.h>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "esp_log.h"

static const char *TAG = "TEST_INPUT";

void app_main(void)
{
    ESP_LOGI(TAG, "USB-Serial/JTAG Input Test");
    ESP_LOGI(TAG, "============================");
    ESP_LOGI(TAG, "Please type something and press Enter:");
    ESP_LOGI(TAG, "The program will echo your input back.");
    ESP_LOGI(TAG, "");

    char buffer[128];
    
    while (1) {
        printf("> ");
        fflush(stdout);
        
        // Read a line from stdin
        if (fgets(buffer, sizeof(buffer), stdin) != NULL) {
            // Remove trailing newline
            size_t len = strlen(buffer);
            if (len > 0 && buffer[len - 1] == '\n') {
                buffer[len - 1] = '\0';
            }
            
            ESP_LOGI(TAG, "Received: [%s]", buffer);
            ESP_LOGI(TAG, "Length: %d bytes", (int)strlen(buffer));
            
            if (strlen(buffer) > 0) {
                printf("Echo: %s\r\n", buffer);
                fflush(stdout);
            }
        }
        
        vTaskDelay(pdMS_TO_TICKS(10));
    }
}