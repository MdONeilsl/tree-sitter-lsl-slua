default
{
    state_entry()
    {
        integer a = 7;
        integer b = a & 3 | a & 5;
        integer c = (a | 3) & (a | 5);
        integer d = a | (a & 5);
        integer e = a & 2 && a & 4;
    }
}