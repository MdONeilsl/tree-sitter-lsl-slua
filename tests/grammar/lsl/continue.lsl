default
{
    state_entry()
    {
        integer i;
        for (i = 0; i < 10; ++i)
        {
            if (i % 2 == 0) continue;
            llSay(0, (string)i);
        }

        i = 0;
        while (i < 10)
        {
            ++i;
            if (i == 5) continue;
            llSay(0, (string)i);
        }
    }
}