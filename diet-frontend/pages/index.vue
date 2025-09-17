<script setup lang="ts">
import { onMounted, onUnmounted } from 'vue'

// ライフサイクルフック内でDOM操作を適切に管理
onMounted(() => {
  // プリロード状態を削除
  document.body.classList.remove('is-preload')
  
  // タッチムーブとオリエンテーション変更のイベントリスナーを追加
  const handleTouchMove = (e: TouchEvent) => {
    e.preventDefault()
    return false
  }
  
  const handleOrientationChange = () => {
    document.body.scrollTop = 0
  }
  
  document.addEventListener('touchmove', handleTouchMove, { passive: false })
  window.addEventListener('orientationchange', handleOrientationChange)
  
  // クリーンアップ関数を保存
  onUnmounted(() => {
    document.removeEventListener('touchmove', handleTouchMove)
    window.removeEventListener('orientationchange', handleOrientationChange)
  })
})
</script>

<template>
<!--
	Aerial by HTML5 UP
	html5up.net | @ajlkn
	Free for personal and commercial use under the CCA 3.0 license (html5up.net/license)
-->
	<head>
		<title>Aerial by HTML5 UP</title>
		<meta charset="utf-8" />
		<meta name="viewport" content="width=device-width, initial-scale=1, user-scalable=no" />
		<link rel="stylesheet" href="assets/css/main.css" />
		<noscript><link rel="stylesheet" href="assets/css/noscript.css" /></noscript>
	</head>
	<body class="is-preload">
		<div id="wrapper">
			<div id="bg"></div>
			<div id="overlay"></div>
			<div id="main">

				<!-- Header -->
					<header id="header">
						<h1>Adam Jensen</h1>
						<p>Security Chief &nbsp;&bull;&nbsp; Cyborg &nbsp;&bull;&nbsp; Never asked for this</p>
						<nav>
							<ul>
								<li><a href="#" class="icon brands fa-twitter"><span class="label">Twitter</span></a></li>
								<li><a href="#" class="icon brands fa-facebook-f"><span class="label">Facebook</span></a></li>
								<li><a href="#" class="icon brands fa-dribbble"><span class="label">Dribbble</span></a></li>
								<li><a href="#" class="icon brands fa-github"><span class="label">Github</span></a></li>
								<li><a href="#" class="icon solid fa-envelope"><span class="label">Email</span></a></li>
							</ul>
						</nav>
					</header>

				<!-- Footer -->
                <footer id="footer">
                    <span class="copyright">&copy; Untitled. Design: <a href="http://html5up.net">HTML5 UP</a>.</span>
                </footer>

			</div>
		</div>
	</body>
</template>
<!-- 
<template>
  <div>
    <div>
      Hello!
    </div>
    <div>
      <NuxtLink to="/foo">
        Foo
      </NuxtLink>
    </div>
  </div>
</template> -->