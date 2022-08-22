#!/usr/bin/expect

# :@Author WangYH
# :@Date 2021/09/25 PM 4:00
# :@Desc 实现接收参数登陆Ssh；配合Iterm效果奇佳

set timeout 30

spawn ssh -p [lindex $argv 0] [lindex $argv 1]@[lindex $argv 2]
expect {
        "(yes/no)?"
        {send "yes\n";exp_continue}
        "password:"
        {send "[lindex $argv 3]\n"}
}
interact

