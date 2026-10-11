#pragma once
#include "counter.hpp"
#include "freertos/FreeRTOS.h"
#include "freertos/queue.h"
struct InputEvent {Key key; uint32_t at_ms;};
namespace buttons {
void init();
bool select_pressed();
void start(QueueHandle_t queue);
}
