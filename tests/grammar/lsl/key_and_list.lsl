key  gK = TEXTURE_BLANK;
list gL = [gK, ""];

default
{
    state_entry()
    {
        llOwnerSay((string)llGetListEntryType(gL, 0));
        llOwnerSay((string)llListFindList(gL, (list)gK));
    }
}