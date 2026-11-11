integer add(integer a, integer b)
{
    return a + b;
}

float average(float a, float b)
{
    return (a + b) / 2.0;
}

default
{
    state_entry()
    {
        integer x = add(1, 2);
        float   y = average(3.0, 4.0);
        llSay(0, (string)x);
    }
}