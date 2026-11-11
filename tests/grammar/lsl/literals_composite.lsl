vector   gV = <1.0, 2.0, 3.0>;
rotation gR = <0.0, 0.0, 0.0, 1.0>;
list     gL = [1, 2.0, "three", <4.0, 5.0, 6.0>];
list     gEmpty = [];

default
{
    state_entry()
    {
        vector v = <-1.0, 0.0, 1.5>;
        rotation r = <0.0, 0.0, 0.7071, 0.7071>;
        list l = [1, 2, 3];
    }
}