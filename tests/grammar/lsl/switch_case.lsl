integer gValue = 2;

default
{
    state_entry()
    {
        switch (gValue)
        {
            case 1: llSay(0, "one");
            case 2: llSay(0, "two");
            case 3:
            {
                llSay(0, "three");
                break;
            }
            default: llSay(0, "many");
        }
    }
}