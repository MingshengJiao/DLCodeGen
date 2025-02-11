client_names=(gpt-4o-mini deepseekcoder)

target_files=()

# 检查两个列表长度
if [ ${#client_names[@]} -ne ${#target_files[@]} ]; then
  echo "client names和target_files的数量不匹配"
  exit 1
fi

# 遍历列表对应元素
for i in "${!client_names[@]}"; do
    client_name=${client_names[$i]}
    target_file=${target_files[$i]}

    echo "Running: python3 main_compare_generation.py --client_name $client_name --generate_method_name comparison --target_file $target_file &"
    python3 main_compare_generation.py --client_name $client_name --generate_method_name comparison --target_file $target_file &
    if [ $? -ne 0 ]; then
        echo "Running failed: $client_name: $target_file"
    else
        echo "Running success: $client_name: $target_file"
    fi
done

wait

echo "All process finished!"
