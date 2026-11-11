#define A 1
#define B(x) (x + 1)
#undef A
#include "file.lsl"

#ifdef DEBUG
integer gDebug = 1;
#else
integer gDebug = 0;
#endif

#ifndef NDEBUG
integer gNot = 1;
#endif

#if 1
integer gIf = 1;
#elif 0
integer gElif = 2;
#else
integer gElse = 3;
#endif

#warning "careful"
#error "not really"

default
{
    state_entry()
    {
    }
}