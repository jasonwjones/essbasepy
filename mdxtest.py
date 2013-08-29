import Essbase
esb = Essbase.Essbase()

print "Connecting..."
esb.connect('admin','Way2GoGuys', 'epm11123')
print "Connected..."

#stmts = [
#    "display user hypuser",
#    "select { ([Year].[Qtr1], [Product].[100]) , ([Year].[Qtr2], [Product].[200]) } on columns from Sample.Basic where ([Measures].[Profit])",
#    "select { ([Year].[Qtr1], [Product].[100]) , ([Year].[Qtr2], [Product].[200]) } on columns, {[Market].[East], [Market].[West]} on rows from Sample.Basic where ([Measures].[Profit])",
#    "select [Year].Members properties level_number, gen_number on columns, [Product].Members properties member_alias on rows from Sample.Basic",
#    "display user essbatch",
#]

#for stmt in stmts:
#    esb.execute(stmt)

#esb.execute("display user hypuser")
esb.execute("display database Sample.Basic")
esb.do("display database Sample.Basic")
print esb.pop_msg()

print "Disconnecting..."
esb.disconnect()

