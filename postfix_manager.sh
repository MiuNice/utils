#!/bin/bash

# Postfix 主配置文件路径
POSTFIX_MAIN_CF="/etc/postfix/main.cf"

# 重载 postfix
function reload_postfix() {
    echo "重载 Postfix 配置..."
    sudo postfix reload
    echo "完成。"
}

# 显示 mynetworks 配置
function show_mynetworks() {
    echo "当前 mynetworks 配置："
    local current=$(postconf -h mynetworks)
    IFS=',' read -ra nets <<< "$current"
    for net in "${nets[@]}"; do
        local trimmed_net=$(echo "$net" | xargs)
        echo " - $trimmed_net"
    done
}

# 添加 IP 到 mynetworks
function add_network() {
    local ip=$1
    if [[ -z "$ip" ]]; then
        echo "请提供要添加的 IP 或网段"
        exit 1
    fi

    local current=$(postconf -h mynetworks)
    IFS=',' read -ra nets <<< "$current"

    for net in "${nets[@]}"; do
        if [[ "$(echo "$net" | xargs)" == "$ip" ]]; then
            echo "$ip 已在 mynetworks 中。"
            return
        fi
    done

    nets+=("$ip")
    local new_value=$(printf "%s, " "${nets[@]}")
    new_value="${new_value%, }"  # 去掉最后一个逗号和空格

    echo "添加 $ip 到 mynetworks"
    sudo postconf -e "mynetworks = $new_value"
    reload_postfix
}

# 从 mynetworks 中删除 IP
function remove_network() {
    local ip=$1
    if [[ -z "$ip" ]]; then
        echo "请提供要删除的 IP 或网段"
        exit 1
    fi

    local current=$(postconf -h mynetworks)
    IFS=',' read -ra nets <<< "$current"

    local new_nets=()
    local found=0
    for net in "${nets[@]}"; do
        if [[ "$(echo "$net" | xargs)" == "$ip" ]]; then
            found=1
        else
            new_nets+=("$(echo "$net" | xargs)")
        fi
    done

    if [[ $found -eq 0 ]]; then
        echo "$ip 不在 mynetworks 中。"
        return
    fi

    local new_value=$(printf "%s, " "${new_nets[@]}")
    new_value="${new_value%, }"

    echo "从 mynetworks 删除 $ip"
    sudo postconf -e "mynetworks = $new_value"
    reload_postfix
}

# 命令分发
function usage() {
    echo "用法: $0 source {show|add|remove} [IP/网段]"
    exit 1
}

if [[ "$1" == "source" ]]; then
    case $2 in
        show)
            show_mynetworks
            ;;
        add)
            add_network "$3"
            ;;
        remove)
            remove_network "$3"
            ;;
        *)
            usage
            ;;
    esac
else
    usage
fi
