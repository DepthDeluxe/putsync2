import Vue from 'vue'
import VueResource from 'vue-resource'
import ElementUI from 'element-ui'
import locale from 'element-ui/lib/locale/lang/en'
import 'element-ui/lib/theme-chalk/index.css'

import App from './components/App.vue'
import ConfigurationForm from './components/ConfigurationForm.vue'
import router from './router'

Vue.use(VueResource)
Vue.use(ElementUI, {locale})

Vue.component('configuration-form', ConfigurationForm)

new Vue({
    el: '#app',
    router,
    render: h => h(App)
})
