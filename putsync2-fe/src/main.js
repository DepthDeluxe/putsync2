import Vue from 'vue'
import VueResource from 'vue-resource'
import ElementUI from 'element-ui'
import locale from 'element-ui/lib/locale/lang/en'
import 'element-ui/lib/theme-chalk/index.css'

import App from './components/App.vue'
import router from './router'

Vue.use(VueResource)
Vue.use(ElementUI, {locale})

new Vue({
    el: '#app',
    router,
    render: h => h(App)
})
