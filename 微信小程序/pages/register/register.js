// pages/register/register.js
var util = require('../../utils/util.js'); 

Page({

  /**
   * 页面的初始数据
   */
  data: {
    hint_finished: '',
    remain_time: 5,
    warning_time: 5,
    isSendHidden: false,
    isWaitHidden: true,
    isLoading: false,
    // email: '',
    email: '806205254@qq.com',    
    username: '',
    password: '',
    confirm_password: '',
    captcha: '',
    warning: '',
  },


  /**
   * 生命周期函数--监听页面加载
   */
  onLoad: function (options) {
  
  },

  /**
   * 生命周期函数--监听页面初次渲染完成
   */
  onReady: function () {

  },

  /**
   * 生命周期函数--监听页面显示
   */
  onShow: function () {
  
  },

  /**
   * 生命周期函数--监听页面隐藏
   */
  onHide: function () {
  
  },
  set_email: function(e){
    this.setData({
      email: e.detail.value
    })
  },
  set_username: function (e) {
    this.setData({
      username: e.detail.value
    })
  },
  set_password: function (e) {
    // console.log(e.detail.value)
    var val = e.detail.value.slice(-1)
    if (val == '`' || val == '~' || val == ',' || val == '.' || val == '{' || val == '}' || val == ';' || val == ':' || val == '[' || val == ']' || val == '/' || val == '?'){
      util.show_warning(this, '密码不能包含`~.,;:[]{}/?', 5)  
      this.setData({
        password: e.detail.value.slice(0,-1)
      })  
    }
    else {
      this.setData({
        password: e.detail.value
      })
    }
  },
  check_password: function(e){
    if (e.detail.value.length < 8 || e.detail.value.length > 32){
      util.show_warning(this, '密码长度应在8到32之间', 3)        
    }
  },
  set_confirm_password: function (e) {
    this.setData({
      confirm_password: e.detail.value
    })
  },
  set_captcha: function (e) {
    this.setData({
      captcha: e.detail.value,
    })
  },
  send_captcha: function(){
    var that = this
    if (that.data.email == ''){
      util.show_warning(this, '邮箱不能为空！', 5)
    }
    else {
      that.setData({
        isSendHidden: true,
        isWaitHidden: false,
        hint_finished: '     验证码已发送到邮箱',
      })
      wx.request({
        url: 'http://120.77.207.13:1115/send_captcha',
        method: 'POST',
        header: {
          'content-type': 'application/json'
        },
        
        data: JSON.stringify({"email": that.data.email}) , //对字典序列化
        success: function (res) {
          console.log(res.data)
        }
      })
      var interval = setInterval(function () {
        this.setData({
          remain_time: that.data.remain_time - 1,
        });
        if (that.data.remain_time == 0) {
          that.setData({
            isSendHidden: false,
            isWaitHidden: true,
            remain_time: 5,
            hint_finished: '',
          })
          clearInterval(interval);
        }
      }.bind(this), 1000);
    }
  },
  register: function(){
    
    var that = this
    
    if (that.data.captcha == ''){
      util.show_warning(that, '验证码不能为空！', 5)
    }
    else if (that.data.password == ''){
      util.show_warning(that, '密码不能为空！', 5)
    }
    else if (that.data.username == ''){
      util.show_warning(that, '用户名不能为空！', 5)
    }
    else if (that.data.email == ''){
      util.show_warning(that, '邮箱不能为空！', 5)
    }
    else if (that.data.password != that.data.confirm_password){ //两次输入的密码不一致
      util.show_warning(that, '两次输入的密码不一致！', 5)
    }
    else {
      that.setData({
        isLoading: true,
      })
      wx.request({
        url: 'http://120.77.207.13:1115/register',
        method: 'POST',
        header: {
          'content-type': 'application/json'
        },
        data: JSON.stringify({
           "email": that.data.email,
           "username": that.data.username,
           "password": that.data.password,
           "captcha": that.data.captcha
           }),
        success: function(res){
          console.log(res.data)
        }
      })
    }
  }




})