Page({
  data:{
    email: '806205254@qq.com',
    password: '12345678', 
    isLoading: false,
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
  login: function(){
    var that = this
    that.setData({
      isLoading: true
    })
    wx.request({
      url: 'http://120.77.207.13:1115/login',
      method: 'POST',
      header: {
        'content-type': 'application/json'
      },
      data: JSON.stringify({
        "email": that.data.email,
        "password": that.data.password,
      }),
      success: function (res) {
        console.log(res.data)
        if (res.data['status_code'] == 'welcome'){
          wx.setStorage({
            key: 'userInfo',
            data: { "email": that.data.email, "password": that.data.password },
          })
          wx.navigateTo({
            url: '/pages/first/select/select',
          })
        }
        else if (res.data['status_code'] == 'wrong_password'){
          wx.showModal({
            title: '登录失败',
            content: '请检查密码是否正确',
          });
        }
        else if (res.data['status_code'] == 'notexist') {
          wx.showModal({
            title: '登录失败',
            content: '用户不存在！',
          });
        }
        that.setData({
          isLoading: false
        })
      }
    })
  },
  onShareAppMessage: function () {

  }
})