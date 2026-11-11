default
{
    state_entry()
    {
        integer a = 1;
        if (a > 0) { a = 1; }
        if (a > 0) { a = 1; } else { a = 2; }
        if (a == 1) { a = 1; }
        else if (a == 2) { a = 2; }
        else { a = 0; }
        if (a > 0) a = 1;
        if (a > 0) a = 1; else a = 2;
    }
}