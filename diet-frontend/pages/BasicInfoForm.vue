<template>
    <div class="container">
        <ClientOnly>
            <div id="background" style="width: 100%; height: 100vh; position: fixed; top: 0; left: 0; z-index: -1;"></div>
        </ClientOnly>
        <div class="card mx-auto my-5 shadow-lg w-75" style="width: 75%;">
            <div class="card-body">    
                <h3 class="card-title text-center">
                    あなたのことを教えてください
                </h3>
                <form @submit.prevent="handleSubmit">
                    <div class="row align-items-stretch">
                        <!-- 左側: 写真アップロード -->
                        <div class="form-group col-md-6 d-flex flex-column">
                            <label for="user-picture" class="mb-2 fs-3">
                                現在のあなた
                            </label>
                            <small class="form-text text-muted mb-3">
                                あなたの正面から見た顔の画像を選択してください
                            </small>
                            <input
                                id="user-picture"
                                type="file"
                                class="form-control mb-3"
                                accept="image/*"
                                @change="handleFileUpload"
                            />

                            <!-- プレビュー領域 -->
                            <div class="preview-field d-flex justify-content-center align-items-center border" style="height: 500px; overflow: hidden;">
                                <div v-if="previewUrl" class="d-flex justify-content-center align-items-center w-100 h-100">
                                    <img
                                    :src="previewUrl"
                                    alt="preview"
                                    class="img-thumbnail"
                                    style="height: 100%; width: auto; object-fit: contain;"
                                    />
                                </div>
                                <div v-else class="text-muted text-center">
                                    画像がここに表示されます
                                </div>
                            </div>
                        </div>

                        <!-- 右側: 入力フォーム -->
                        <div class="col-md-6 py-3 d-flex flex-column">
                            <div class="form-group my-3">
                            <label for="user-name">名前</label>
                            <input
                                id="user-name"
                                class="form-control"
                                type="text"
                                placeholder="名前を入力してください"
                                v-model="form.name"
                                
                            />
                            </div>

                            <div class="form-group my-3">
                                <label for="user-height">身長</label>
                                <div class="input-group">
                                <input
                                    id="user-height"
                                    class="form-control"
                                    type="number"
                                    min="0"
                                    max="300"
                                    placeholder="身長を入力してください"
                                    v-model="form.height"
                                />
                                <span class="input-group-text">cm</span>
                                </div>
                            </div>

                            <div class="form-group my-3">
                                <label for="user-age">年齢</label>
                                <div class="input-group">
                                <input
                                    id="user-age"
                                    class="form-control"
                                    type="number"
                                    min="0"
                                    max="200"
                                    placeholder="年齢を入力してください"
                                    v-model="form.age"
                                />
                                <span class="input-group-text">歳</span>
                                </div>
                            </div>

                            <div class="form-group my-3">
                                <label for="gender">性別</label>
                                <select id="gender" class="form-select" v-model="form.gender">
                                    <option disabled value="">選択してください</option>
                                    <option value="male">男性</option>
                                    <option value="female">女性</option>
                                    <option value="none">秘密</option>
                                </select>
                            </div>

                            <div class="form-group my-5">
                                <label for="user-weight-ideal">理想の体重</label>
                                <div class="input-group">
                                <input
                                    id="user-weight-ideal"
                                    class="form-control"
                                    type="number"
                                    placeholder="1ヶ月後に目指す体重を入力してください"
                                    v-model="form.weight_ideal"
                                    
                                />
                                <span class="input-group-text">kg</span>
                                </div>
                            </div>
                        </div>
                    </div>

            
                    <!-- ボタン -->
                    <div class="row mt-3 mx-auto">
                        <button type="submit" class="btn btn-primary w-50 mx-auto fs-4">
                            更新・登録
                        </button>
                    </div>
                </form>
        
                <!-- デバッグ -->
                <!-- <pre>{{ form }}</pre> -->
            </div>
        </div>
    </div>
</template>

<script setup>
    // bootstrap import部分
    import { useHead, navigateTo } from '#app'
    useHead({
        link: [
            {
                rel: 'stylesheet',
                href: 'https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css'
            }
        ],
        script: [
            {
                src: 'https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js',
                defer: true
            }
        ],
        // 背景画像
        script: [
            {
                src: 'https://cdnjs.cloudflare.com/ajax/libs/trianglify/2.0.0/trianglify.min.js',
                defer: true
            }
        ],
    })

    import { reactive, ref } from "vue"
    const form = reactive({
            name: "",
            age: "",
            height: "",
            gender: "",
            weight_ideal: "",
            picture: "",
            // exercise_time: "",
            // sleep_time: "",
            user_id: "user123",   // 任意で付与
            session_id: "sess001" // 任意で付与
        });
    const previewUrl = ref(null)

    // 写真表示
    function handleFileUpload(event) {
        const file = event.target.files[0];
        if (!file) return;

        const reader = new FileReader();
        reader.onload = () => {
            // "data:image/jpeg;base64,..." の形式 → "," 以降を抽出
            const base64Data = reader.result;
            form.picture = base64Data; // ここに Base64 を格納
            previewUrl.value = URL.createObjectURL(file); // 画像プレビューはそのまま
        };
        reader.readAsDataURL(file);
    }

    // submit
    const responseData = ref(null);
    const isLoading = ref(false)

    const handleSubmit = async () => {
        try {
            // for (const key in form) {
            //     if (!form[key]) {
            //         alert("全ての項目を入力してください");
            //         return; // 空欄があれば送信中止
            //     }
            // }

            isLoading.value = true

            // FormDataを作成してファイルとフォームデータを送信
            const formData = new FormData()
            Object.keys(form).forEach(key => {
                formData.append(key, form[key])
            });
            // formData.append('name', form.name)
            // formData.append('age', form.age)
            // formData.append('height', form.height)
            // formData.append('gender', form.gender)

            // formData.append('face_image', form.picture) // 現在は同じ画像を使用
            // formData.append('user_id', 'user_123') // 適宜ユーザーIDを設定
            // formData.append('session_id', `session_${Date.now()}`) // セッションIDを生成

            console.log('Sending request to API...')

            try {
                console.log(JSON.stringify(form))
                // 本番のAPI呼び出し
                const response = await $fetch('http://127.0.0.1:8000/init', {
                    method: 'POST',
                    body: JSON.stringify(form), // JSONで送信
                    headers: {
                        'Content-Type': 'application/json'
                    },
                })

                // 成功時の処理
                console.log('API Response:', response)
                alert('データ送信完了しました！')

                // main画面に遷移
                await navigateTo('/DailyLogForm')

            } catch (apiError) {
                // APIが利用できない場合はダミーデータで続行
                console.warn('API呼び出しに失敗しました。ダミーデータで続行します:', apiError)

                const dummyResponse = {
                    answer: "ダミーの解析結果です",
                    meta: formData,
                }

                console.log('Using dummy response:', dummyResponse)
                alert('送信完了 ダミーデータ')

                // 結果画面に遷移
                await navigateTo('/DailyLogForm')
            }

        } catch (err) {
            console.error('Request failed:', err)

            // より詳細なエラー情報を表示
            let errorMessage = 'リクエストに失敗しました'
            if (err.response) {
                console.error('Response status:', err.response.status)
                console.error('Response data:', err.response._data)
                errorMessage = `サーバーエラー (${err.response.status}): ${err.response._data?.detail || err.response.statusText}`
            } else if (err.message) {
                errorMessage = err.message
            }

            alert(errorMessage)
        } finally {
            isLoading.value = false
        }
    };
        //alert(`お名前: ${form.name}\n身長: ${form.height}cm\n年齢: ${form.age}歳\n理想の体重: ${form.weight_ideal}kg\n写真: ${form.picture?.name || "なし"}`);

        // const fd = new FormData();
        // fd.append("user_id", form.user_id);
        // fd.append("session_id", form.session_id);
        // // フォーム情報を JSON 文字列にして送る
        // fd.append("form_data", JSON.stringify({
        //     name: form.name,
        //     age: form.age,
        //     height: form.height,
        //     gender: form.gender,
        //     weight: form.weight,
        //     exercise_time: form.exercise_time,
        //     sleep_time: form.sleep_time
        // }));

        // try {
        //     const res = await axios.post("http://localhost:8000/generate-answer", fd, {
        //         headers: { "Content-Type": "multipart/form-data" }
        //     });
        //     responseData.value = res.data;
        // } catch (err) {
        //     console.error(err);
        //     alert("送信に失敗しました");
// }
        
    // 背景画像
    import { onMounted, onUnmounted, nextTick } from "vue";
    function drawBackground() {
        const target = document.getElementById("background");
        if (!target) return;

        // 前回のSVGを削除
        target.innerHTML = "";

        const rect = target.getBoundingClientRect();
        const width = rect.width || 1;
        const height = rect.height || 1;

        const pattern = window.Trianglify({
            width,
            height,
            cell_size: 100,
            x_colors: "Blues",
            y_colors: "Blues",
        });

        target.appendChild(pattern.svg());
    }
    onMounted(async () => {
        await nextTick();
        // 初回描画
        drawBackground();
        // リサイズ時にも描画
        window.addEventListener("resize", drawBackground);
    });
    onUnmounted(() => {
        window.removeEventListener("resize", drawBackground);
    });
</script>

<style lang="css" scoped>
    .form-group:has(input:required) > label::after {
        content: " *";
        color: red;
        margin-left: 2px;
    }
    .form-group:has(select:required) > label::after {
        content: " *";
        color: red;
        margin-left: 2px;
    }
</style>