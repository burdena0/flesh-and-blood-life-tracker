#pragma once
#include <cstdint>
// Send bit 7 first so the latched QA..QH outputs map to A..DP.
template<class WriteData, class WriteClock, class WriteLatch, class Delay>
void shift_segments(uint8_t value, WriteData data, WriteClock clock,
                    WriteLatch latch, Delay delay) {
    latch(0);
    for(int bit=7;bit>=0;--bit){
        clock(0);data((value>>bit)&1);delay();
        clock(1);delay();
    }
    clock(0);latch(1);delay();latch(0);
}
