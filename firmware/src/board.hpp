#pragma once
#include "driver/gpio.h"
#include "sdkconfig.h"
#if !CONFIG_IDF_TARGET_ESP32S3
#error This wiring requires a Waveshare ESP32-S3-Zero.
#endif
namespace board {
inline constexpr gpio_num_t serial_data=GPIO_NUM_43;
inline constexpr gpio_num_t shift_clock=GPIO_NUM_1;
inline constexpr gpio_num_t latch_clock=GPIO_NUM_2;
inline constexpr gpio_num_t digits[]={GPIO_NUM_4,GPIO_NUM_5,GPIO_NUM_6,GPIO_NUM_7};
inline constexpr gpio_num_t buttons[]={GPIO_NUM_8,GPIO_NUM_9,GPIO_NUM_10,GPIO_NUM_11};
inline constexpr gpio_num_t resource_leds[]={GPIO_NUM_12,GPIO_NUM_13,GPIO_NUM_44};
// GPIO3, USB19/20, onboard RGB21 and all underside pads are unused.
}
