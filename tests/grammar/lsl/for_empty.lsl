default
{
    state_entry()
    {
        integer i = 0;
        for (; i < 10 ;) { ++i; }
        for (i = 0; ; ) { ++i; if (i > 10) break; }
        for (; ; ) { break; }
        for (i = 0; i < 10; ) { ++i; }
        for (i = 0; ; ++i) { if (i > 10) break; }
    }
}