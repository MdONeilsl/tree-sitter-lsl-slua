default
{
    state_entry()
    {
        key owner = llGetOwner();
        integer info = llGetAgentInfo(owner);
        llOwnerSay(llList2String(llGetObjectDetails(llGetKey(), []), 0));
    }
}