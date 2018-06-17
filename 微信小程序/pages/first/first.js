Page({
  data:{
    email: '',
    password: '',
  },
  set_email: function (e) {
    this.setData({
      email: e.detail.value
    })
  },
  set_password: function (e) {
    this.setData({
      password: e.detail.value
    })
  },
  onShareAppMessage: function () {

  }
})