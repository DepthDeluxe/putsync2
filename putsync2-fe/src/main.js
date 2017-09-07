import Vue from 'vue'
import ElementUI from 'element-ui'
import VueResource from 'vue-resource'
import 'element-ui/lib/theme-default/index.css'

import App from './components/App.vue'
import router from './router'

Vue.use(ElementUI)
Vue.use(VueResource)

new Vue({
    el: '#app',
    router,
    render: h => h(App)
})
