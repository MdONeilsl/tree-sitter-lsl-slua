// single line

/*
 block
*/

/**/

default
{
    state_entry()
    {
        integer x = 1; // trailing
        /* inline */ integer y = 2;
        /* before */
        llSay(0, "hi"); /* after */
    }
}