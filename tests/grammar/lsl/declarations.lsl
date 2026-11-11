integer gA = 1;
integer gB;

default
{
    state_entry()
    {
        integer local1 = 10;
        integer local2;
        string s = "x";
        s = "y";
        local1 += 5;
        local1 -= 2;
        local1 *= 3;
        local1 /= 2;
        local1 %= 7;
    }
}