import Vue from 'vue'
import ElementUI from 'element-ui'
import VueResource from 'vue-resource'
import 'element-ui/lib/theme-default/index.css'

import App from './components/App.vue'
import router from './router'

import DownloadHistoryTable from './components/DownloadHistoryTable.vue'
import ActiveDownloadTable from './components/ActiveDownloadTable.vue'

Vue.use(ElementUI)
Vue.use(VueResource)

Vue.component('download-history-table', DownloadHistoryTable)
Vue.component('active-download-table', ActiveDownloadTable)

new Vue({
    el: '#app',
    router,
    render: h => h(App)
})
