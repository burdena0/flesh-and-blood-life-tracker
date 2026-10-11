#pragma once
#include "counter.hpp"
namespace display {
void init();
void publish(const Frame &frame);
void self_test();
}
