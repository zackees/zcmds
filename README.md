# productivity_cmds
Cross platform(ish) productivity commands written in python

For mac home/end bindings write out

~/Library/KeyBindings/DefaultKeyBinding.dict:

```{
    "\UF729"  = moveToBeginningOfLine:; // home
    "\UF72B"  = moveToEndOfLine:; // end
    "$\UF729" = moveToBeginningOfLineAndModifySelection:; // shift-home
    "$\UF72B" = moveToEndOfLineAndModifySelection:; // shift-end
}```
