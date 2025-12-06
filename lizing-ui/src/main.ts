// import { createApp } from 'vue'
// import './style.css'
// import App from './App.vue'
//
// import './assets/main.css'
//
//
// // createApp(App).mount('#app')
//
// const app = createApp(App)
// app.use(router)
// app.mount('#app')


import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import './index.css'

createApp(App).use(router).mount('#app')

