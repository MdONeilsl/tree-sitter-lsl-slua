quaternion gQ;

default
{
    state_entry()
    {
        quaternion q = <0.0, 0.0, 0.0, 1.0>;
        quaternion r = (quaternion)"<0.0, 0.0, 0.0, 1.0>";
        (quaternion)ZERO_ROTATION;
    }
}