.assign s = "'hello world'"
.invoke md5 = HASH.MD5(s)
.if (md5.success)
  .print "the md5 of ${s} is ${md5.result}"
.else
  .print "MD5 error"
.end if

.invoke md5 = HASH.MD5("$trmquot{s}")
.if (md5.success)
  .print "the md5 of $trmquot{s} is ${md5.result}"
.else
  .print "MD5 error"
.end if
