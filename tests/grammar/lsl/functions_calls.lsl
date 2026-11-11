default
{
    state_entry()
    {
        llSay(0, "no args");
        llSay(0, "one arg");
        llSay(0, "two args");
        llOwnerSay("owner");
        llSetText("hi", <1.0, 1.0, 1.0>, 1.0);
    }
}