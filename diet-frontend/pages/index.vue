<script setup lang="ts">
import { ref, onMounted } from 'vue'

// レスポンシブなナビゲーションメニューの状態管理
// const isNavbarOpen = ref(false)
const backgroundImageUrl = ref('/images/walking.jpg')

// // ナビゲーションメニューの開閉
// const toggleNavbar = () => {
//   isNavbarOpen.value = !isNavbarOpen.value
// }

// // ボタンのイベントハンドラー
// const handleGetStarted = () => {
//   console.log('Get Started clicked')
//   // TODO: 実際の処理を実装
// }

// const handleReadMore = () => {
//   console.log('Read More clicked')
//   // TODO: 実際の処理を実装
// }

// スクロールイベントでナビゲーションバーの透明度を調整
const handleScroll = () => {
  const navbar = document.querySelector('.navbar')
  if (navbar) {
    if (window.scrollY > 50) {
      navbar.classList.add('navbar-scrolled')
    } else {
      navbar.classList.remove('navbar-scrolled')
    }
  }
}

onMounted(() => {
  window.addEventListener('scroll', handleScroll)
})
</script>

<template class="index-page">
    <div 
      class="page-header min-vh-100"
      :style="{
        backgroundImage: `url(${backgroundImageUrl})`,
        backgroundSize: 'cover',
        backgroundPosition: 'center center',
        backgroundRepeat: 'no-repeat'
      }"
      loading="lazy">
      <span class="mask bg-gradient-dark opacity-5"></span>
      <div class="container">
        <div class="row">
          <div class="col-lg-6 col-md-7 d-flex justify-content-center flex-column">
            <h1 class="text-white mb-4 hero-title">健康状態向上</h1>
            <p class="text-white opacity-8 lead pe-5 me-5 hero-description">
              あなたの健康をサポートします。今すぐ始めましょう！
            </p>
            <div class="buttons">
                <NuxtLink to="/ResultsPage" class="navigator_link">
                    始める
                </NuxtLink>
                <NuxtLink to="/BasicInfoForm" class="navigator_link">
                    プロフィールを入力する
                </NuxtLink>
            </div>
          </div>
        </div>
      </div>
    </div>
</template>

<style lang="css" scoped>
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

.index-page {
  font-family: 'Helvetica Neue', Arial, sans-serif;
  margin: 0;
}
/* ヒーローセクション関連のスタイル */
.page-header {
  position: fixed;
  top: 0;
  left: 0;
  margin: 0;
  height: 100vh;
  width: 100vw;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  background-image: url(${backgroundImageUrl});
  background-size: cover;
  background-position: center center;
  background-repeat: no-repeat;
}

.mask {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: 1;
}

.container {
  position: relative;
  z-index: 2;
  background: rgba(255, 255, 255, 0.7);
  padding: 5vh;
}

.hero-title {
  font-size: 3.5rem;
  font-weight: 700;
  line-height: 1.2;
  margin-bottom: 1.5rem;
  animation: fadeInUp 1s ease-out;
}

.hero-description {
  font-size: 1.25rem;
  line-height: 1.6;
  margin-bottom: 2rem;
  animation: fadeInUp 1s ease-out 0.2s both;
}

.buttons {
  animation: fadeInUp 1s ease-out 0.4s both;
  display: flex;
  justify-content: space-around;
  flex-basis: auto;
}

/* アニメーション */
@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* レスポンシブデザイン */
@media (max-width: 991.98px) {
  .navbar-collapse {
    background-color: rgba(0, 0, 0, 0.95);
    border-radius: 10px;
    margin-top: 1rem;
    padding: 1rem;
  }
  
  .hero-title {
    font-size: 2.5rem;
  }
  
  .hero-description {
    font-size: 1.1rem;
    padding-right: 0 !important;
    margin-right: 0 !important;
  }
}

@media (max-width: 767.98px) {
  .hero-title {
    font-size: 2rem;
  }
  
  .hero-description {
    font-size: 1rem;
  }
  
  .buttons {
    display: flex;
    flex-direction: column;
    align-items: flex-start;
  }
  
  .buttons > * {
    margin-right: 0 !important;
    margin-bottom: 0.5rem;
  }
}

@media (max-width: 575.98px) {
  .hero-title {
    font-size: 1.75rem;
  }
  
  .container {
    padding-left: 1rem;
    padding-right: 1rem;
  }
}

/* アクセシビリティ向上 */
@media (prefers-reduced-motion: reduce) {
  .hero-title,
  .hero-description,
  .buttons {
    animation: none;
  }
  
  .navbar,
  .nav-link {
    transition: none;
  }
}

/* フォーカス管理 */
.nav-link:focus,
.navbar-brand:focus {
  outline: 2px solid rgba(255, 255, 255, 0.8);
  outline-offset: 2px;
}

.navigator_link {
  font-size: 1rem;
  font-weight: 600;
  padding: 0.75rem 1.5rem;
  border-radius: 0.375rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1), 0 1px 2px rgba(0, 0, 0, 0.06);
  transition: all 0.15s ease-in-out;
  color: blue;
  background-color: white;
}

.text-white {
  color: black !important;
  text-align: center;
}
</style>