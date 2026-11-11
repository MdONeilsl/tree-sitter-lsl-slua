default
{
    state_entry()
    {
        integer i = 0;
        while (i < 10) { ++i; }
        do { --i; } while (i > 0);
        for (i = 0; i < 5; ++i) { }
        while (i < 5) ++i;
    }
}