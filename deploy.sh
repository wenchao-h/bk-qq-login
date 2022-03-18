#! /bin/bash

source /data/install/load_env.sh
source ./env.sh

green_echo ()    { echo -e "\033[032;1m$@\033[0m"; }
red_echo () { echo -e "\033[031;1m$@\033[0m"; }
log () {
    echo "$@"
}

files=(add_settings_production.py ee_official_login/qrcode/qq/settings.py)

# 替换模板用的sed文件，执行退出时自动清理掉
trap 'rm -f $sed_script' EXIT TERM
sed_script=$(mktemp /tmp/XXXXXX.sed)

place_holders=( $(cat "${files[@]}" 2>/dev/null | grep -Po '__[A-Z][A-Z0-9]+(_[A-Z0-9]+){0,9}__' | sort -u) )

if [[ ${#place_holders} -eq 0 ]]; then
    log "指定文件中不存在符合规则的占位符"
fi

set +u
for p in "${place_holders[@]}"
do
    k=$(echo "$p" | sed 's/^__//; s/__$//;')
    if ! [ -v $k ];  then 
        red_echo "UNDEFINED PLACE_HOLDER: $p" >&2 
    else
        echo -e "$p -> ${!k}"
        echo "s|$p|${!k}|g" >> "$sed_script"
    fi
done
set -u
unset p k v

for file in "${files[@]}"; do
    # 是否真正替换变量到目标路径
    sed -i -f "$sed_script" $file 
done

if ! grep -qE '^QQ'  ${BK_HOME}/open_paas/login/conf/settings_production.py;
then
    mkdir -p /data/backup
    cp -a ${BK_HOME}/open_paas/login/conf/settings_production.py /data/backup/settings_production.py.bak-$(date +%Y%m%d%H%M)
    log "add to settings_production.py"
    sed -i '/^DEBUG/r add_settings_production.py' ${BK_HOME}/open_paas/login/conf/settings_production.py
    green_echo "add to settings_production.py done"
    echo 
fi

chown -R blueking.blueking ./ 

log "copy ee_login to ${BK_HOME}/open_paas/login/"
rsync -av ee_login ${BK_HOME}/open_paas/login/
green_echo "copy ee_login to ${BK_HOME}/open_paas/login/ done "
echo 

log "copy ee_official_login/ to ${BK_HOME}/open_paas/login/ee_official_login/"
rsync -av ee_official_login/ ${BK_HOME}/open_paas/login/ee_official_login/
green_echo "copy ee_official_login/ to ${BK_HOME}/open_paas/login/ee_official_login/ done"
echo

log "copy templates/ to ${BK_HOME}/open_paas/login/templates/"
rsync -av templates/ ${BK_HOME}/open_paas/login/templates/
green_echo "copy templates/ to ${BK_HOME}/open_paas/login/templates/ done"
echo 

green_echo  "deploy done, please restart login service by execute 'systemctl restart bk-paas-login.service'"