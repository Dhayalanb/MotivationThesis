BUILD_TYPE=release LOG_TYPE=info ./angora_fuzzer -M 0 -A -i ./objdump/input -o objdump/output -j 3 -m llvm -t objdump/objdump.track -- objdump/objdump.fast -x @@
