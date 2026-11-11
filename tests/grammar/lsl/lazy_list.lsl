list gL = [];

default
{
    state_entry()
    {
        gL[0] = "first";
        gL[1] = 42;
        integer i = 2;
        gL[i] = <1.0, 2.0, 3.0>;
        gL[i + 1] = [1, 2, 3];

        string s = gL[0];
        integer n = gL[1];
    }
}