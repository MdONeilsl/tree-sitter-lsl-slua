default
{
    state_entry()
    {
        integer a = 1;
        integer b = 2;
        integer r;

        r = a && b;
        r = a || b;
        r = a | b;
        r = a ^ b;
        r = a & b;
        r = a == b;
        r = a != b;
        r = a < b;
        r = a <= b;
        r = a > b;
        r = a >= b;
        r = a << 1;
        r = a >> 1;
        r = a + b;
        r = a - b;
        r = a * b;
        r = a / b;
        r = a % b;
    }
}