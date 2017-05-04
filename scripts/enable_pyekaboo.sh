#!/usr/bin/env bash
#
# ENABLE_PYEKABOO.SH, Itzik Kotler, See: https://github.com/SafeBreach-Labs/pyekaboo
# ----------------------------------------------------------------------------------
#
# Copyright (c) 2017, SafeBreach
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:
#
#  1. Redistributions of source code must retain the above
# copyright notice, this list of conditions and the following
# disclaimer.
#
#  2. Redistributions in binary form must reproduce the
# above copyright notice, this list of conditions and the following
# disclaimer in the documentation and/or other materials provided with
# the distribution.
#
#  3. Neither the name of the copyright holder
# nor the names of its contributors may be used to endorse or promote
# products derived from this software without specific prior written
# permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS
# AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES,
# INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED.
# IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR
# ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE
# GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER
# IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR
# OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF
# ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

echo "Enabling pyekaboo ..."

HOOK_DIR=`pwd`
HOOKS=0

if [ ! -z "$PYTHONPATH" ]; then
	echo "[!] PYTHONPATH env var is already set (=$PYTHONPATH). Maybe pyekaboo is already enabled?"
else
    if [ ! -z "$1" ] && [ -d "$1" ]; then
        HOOK_DIR=$1
        shift
    fi
	export PYTHONPATH=$HOOK_DIR
	echo "[*] PYTHONPATH env var set! (=$PYTHONPATH)"
fi

for HOOK_FILE in $(ls $HOOK_DIR/*.py* 2> /dev/null); do
    echo "[+] Found $HOOK_FILE ... will be triggerd once a Python program will attempt to: \"import $(basename ${HOOK_FILE%.*})\""
    HOOKS=$((HOOKS+1))
done

if [ $HOOKS == 0 ]; then
    echo "[!] No HOOKS (i.e. Python files) were found! Are you sure $HOOK_DIR is where your hooks are?"
else
    echo "[*] Found $HOOKS hook(s)"
fi

if [ "$1" == "-i" ]; then
	echo "[*] Starting Interactive Mode ..."
	$SHELL
fi
