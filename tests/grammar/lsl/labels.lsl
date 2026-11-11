default
{
    state_entry()
    {
        @top;
        integer x = 0;
        x++;
        if (x < 5) jump top;

        @end;
        jump end;
    }
}