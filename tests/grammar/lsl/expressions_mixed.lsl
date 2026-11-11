default
{
    state_entry()
    {
        integer  x = (1 + 2) * 3;
        string   s = "a" + "b" + "c";
        vector   v = <1.0, 2.0, 3.0> + <1.0, 1.0, 1.0>;
        list     l = [1, 2] + [3, 4];
        integer  y = (integer)3.5;
        string   z = (string)42;
        llSay(0, "test");
        llSay(0, s);
        llOwnerSay(s + z);
    }
}