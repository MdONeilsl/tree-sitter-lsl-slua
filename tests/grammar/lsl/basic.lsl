integer gCounter = 0;

default
{
    state_entry()
    {
        gCounter = 42;
        llSay(0, "Hello");
    }

    touch_start(integer num_detected)
    {
        state running;
    }
}

state running
{
    state_entry()
    {
        llOwnerSay("running");
    }
}