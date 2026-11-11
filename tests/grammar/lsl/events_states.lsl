default
{
    state_entry()
    {
        state running;
    }

    touch_start(integer n)
    {
    }

    timer()
    {
    }
}

state running
{
    state_entry()
    {
    }

    touch_end(integer n)
    {
        state default;
    }
}