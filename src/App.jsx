import { useEffect, useState } from 'react';
import './App.css';
import { marked } from 'marked';

// 在文件顶部配置 marked
marked.setOptions({
  breaks: true,  // 支持换行
  gfm: true,     // 支持 GitHub 风格的 markdown
  mangle: false, // 防止修改某些字符
  headerIds: false, // 防止给标题添加 id
});

function App() {
  const [map, setMap] = useState(null);
  const [attractions, setAttractions] = useState([]);
  const [showModal, setShowModal] = useState(false);
  const [activeTab, setActiveTab] = useState("TRAVEL GUIDE");
  const [inputValue, setInputValue] = useState('');
  const [guide, setGuide] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [currentText, setCurrentText] = useState('');
  const [showRequirementsModal, setShowRequirementsModal] = useState(false);
  const [formData, setFormData] = useState({
    gender: 'female',
    age: '',
    birthday: '',
    groupSize: '',
    companions: [],
    hasChildren: '否',
    childAge: '',
    childHeight: '',
    needsDining: '否',
    visitTime: '',
    additionalNotes: '',
    firstVisit: '否',
    specialDate: '',
    preference: '无特殊偏好',
    characterPreference: '',
    ticketType: '标准票'
  });

  const companionOptions = ["闺蜜", "情侣", "家人", "朋友", "家庭"];

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => {
      // 如果是切换"是否携带儿童"
      if (name === 'hasChildren') {
        return {
          ...prev,
          [name]: value,
          // 如果选择"否"，清空儿童相关字段
          ...(value === '否' ? {
            childAge: '',
            childHeight: ''
          } : {})
        };
      }
      // 其他字段正常更新
      return {
        ...prev,
        [name]: name === 'companions' ? [value] : value
      };
    });
  };

  const handleCompanionChange = (option) => {
    setFormData(prev => ({
      ...prev,
      companions: prev.companions.includes(option)
        ? prev.companions.filter(item => item !== option)
        : [...prev.companions, option]
    }));
  };

  useEffect(() => {
    // 加载景点数据
    fetch('/attractions/all_attractions.json')
      .then(response => response.json())
      .then(data => setAttractions(data))
      .catch(error => console.error('加载景点数据失败:', error));

    // 初始化地图
    const initMap = () => {
      const centerPoint = {
        lng: 121.66680726868965,
        lat: 31.14747202651585
      };
      
      if (!window.BMapGL) {
        console.error('BMapGL 未加载');
        return;
      }

      // 添加延迟确保容器已渲染
      setTimeout(() => {
        try {
          console.log('开始初始化地图...');
          const mapContainer = document.getElementById('map-container');
          console.log('地图容器:', mapContainer);

          const bmap = new window.BMapGL.Map("map-container");
          const point = new window.BMapGL.Point(centerPoint.lng, centerPoint.lat);
          
          // 先设置中心点和缩放级别
          bmap.centerAndZoom(point, 17);
          
          // 等待地图加载完成
          bmap.addEventListener('tilesloaded', () => {
            console.log('地图瓦片加载完成');
            // 强制触发重绘
            bmap.setCenter(point);
          });

          // 启用滚轮缩放
          bmap.enableScrollWheelZoom(true);
          
          // 添加控件
          bmap.addControl(new window.BMapGL.ScaleControl());
          bmap.addControl(new window.BMapGL.NavigationControl());
          
          console.log('地图初始化完成');
          setMap(bmap);
        } catch (error) {
          console.error('地图初始化失败:', error);
        }
      }, 100);
    };

    // 加载百度地图脚本
    const loadBaiduMap = () => {
      console.log('开始加载百度地图脚本...');
      
      // 使用同步方式加载脚本
      const script = document.createElement("script");
      script.src = `https://api.map.baidu.com/api?v=3.0&type=webgl&ak=${import.meta.env.VITE_BAIDU_MAP_KEY}&callback=init`;
      script.async = false; // 设置为同步加载
      
      // 在全局作用域中定义回调函数
      window.init = () => {
        console.log('百度地图初始化回调');
        initMap();
      };
      
      document.head.appendChild(script);
    };

    loadBaiduMap();

    return () => {
      if (map) {
        map.destroy();
      }
    };
  }, []);

  // 添加景点标记
  useEffect(() => {
    if (map && attractions.length > 0) {
      attractions.forEach(attraction => {
        if (attraction.location) {
          const point = new window.BMapGL.Point(attraction.location.lng, attraction.location.lat);
          const marker = new window.BMapGL.Marker(point);
          map.addOverlay(marker);

          const infoWindow = new window.BMapGL.InfoWindow(`
            <div style="padding: 10px">
              <h4 style="margin: 0 0 5px 0">${attraction.attraction_name}</h4>
              <p style="margin: 0; font-size: 12px">${attraction.attraction_description}</p>
            </div>
          `, {
            width: 250,
            height: 100,
            title: attraction.attraction_name
          });

          marker.addEventListener('click', () => {
            map.openInfoWindow(infoWindow, point);
          });
        }
      });
    }
  }, [map, attractions]);

  const blogContent = `
# Plan Your Perfect Disney Adventure

Welcome to Magic Trail, your personal Disney itinerary planner! 🎢✨

## What We Offer

Magic Trail is designed to create the perfect Disney experience tailored just for you. Our AI-powered system takes into account your:

- Preferred attractions
- Available time
- Group composition
- Special requirements

## How It Works

- Tell us your preferences 🎯✨
- Share your constraints 📋⚠️
- Tell us about your companions 👨‍👩‍👧‍👦🎟️
- Get a customized itinerary 🏰🗺️
- Enjoy real-time updates and adjustments 🔄⚡ (⏳ *Coming Soon!*)

## Why Magic Trail?

- **Personalized Experience**: Every itinerary is unique
- **Time-Saving**: Skip the planning hassle
- **Smart Optimization**: Best routes and timing
- **Real-Time Updates**: Stay informed about wait times

Let's make your Disney dreams come true! ✨
`;

  // 添加打字机效果函数
  const typeText = async (text) => {
    const chars = text.split('');
    for (let char of chars) {
      await new Promise(resolve => setTimeout(resolve, 50)); // 控制打字速度
      setCurrentText(prev => prev + char);
    }
  };

  const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'https://你的后端域名/api';

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    setGuide('');
    setShowRequirementsModal(false);
    
    try {
      // 构建基本信息
      let inputFields = [
        `性别: ${formData.gender}`,
        `年龄: ${formData.age}`,
        `生日: ${formData.birthday}`,
        `同行人数: ${formData.groupSize}`,
        `同行人身份: ${formData.companions.join(', ')}`,
        `是否携带儿童: ${formData.hasChildren}`
      ];

      // 只在选择携带儿童时添加儿童信息
      if (formData.hasChildren === '是') {
        inputFields.push(`儿童年龄: ${formData.childAge}`);
        inputFields.push(`儿童身高: ${formData.childHeight}`);
      }

      // 添加其他字段
      inputFields = inputFields.concat([
        `是否有就餐需要: ${formData.needsDining}`,
        `预计游玩时长: ${formData.visitTime}`,
        `是否首次入园: ${formData.firstVisit}`,
        `特殊日期: ${formData.specialDate}`,
        `游玩偏好: ${formData.preference}`,
        `人物偏好: ${formData.characterPreference}`,
        `门票类型: ${formData.ticketType}`,
        `其它备注: ${formData.additionalNotes}`
      ]);

      const userInput = inputFields.join('\n');

      const response = await fetch(`${API_BASE_URL}/api/travel_guide`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ 'input-guide': userInput }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const reader = response.body.getReader();
      const decoder = new TextDecoder('utf-8', { fatal: false });
      
      setIsLoading(false);
      
      let buffer = '';
      let currentContent = '';

      while (true) {
          const { done, value } = await reader.read();
          if (done) break;
          
          buffer += decoder.decode(value, { stream: true });
          
          const lines = buffer.split('\n');
          buffer = lines.pop() || '';
          
          for (const line of lines) {
              if (line.startsWith('data: ')) {
                  try {
                      const jsonData = JSON.parse(line.slice(6));
                      if (jsonData.content) {
                          currentContent += jsonData.content;
                          try {
                              const htmlContent = marked.parse(currentContent);
                              setGuide(htmlContent);
                          } catch (markdownError) {
                              console.warn('Markdown 解析错误:', markdownError);
                              setGuide(currentContent); // 降级处理：直接显示原文
                          }
                      }
                  } catch (e) {
                      console.warn('解析数据时出错:', e);
                      continue;
                  }
              }
          }
      }
      
      if (buffer) {
          try {
              if (buffer.startsWith('data: ')) {
                  const jsonData = JSON.parse(buffer.slice(6));
                  if (jsonData.content) {
                      currentContent += jsonData.content;
                      try {
                          const htmlContent = marked.parse(currentContent);
                          setGuide(htmlContent);
                      } catch (markdownError) {
                          console.warn('Markdown 解析错误:', markdownError);
                          setGuide(currentContent);
                      }
                  }
              }
          } catch (e) {
              console.warn('处理剩余数据时出错:', e);
          }
      }
    } catch (error) {
        console.error('Error:', error);
        setGuide(`发生错误: ${error.message}`);
    } finally {
        setIsLoading(false);
    }
  };

  // 使用防抖的方式处理滚动
  useEffect(() => {
    const element = document.querySelector('.input-guide-content');
    if (element) {
        element.scrollTop = element.scrollHeight;
    }
  }, [guide]);

  console.log('API Base URL:', API_BASE_URL);

  return (
    <div className="container">
      <header className="header">
        <div className="header-content">
          <div className="header-left"></div>
          <h1>Magic Trail</h1>
          <div className="header-logos">
            <img src="/assets/media/ATF logo_White.png" alt="ATF Logo" className="logo-atf" />
            <img src="/assets/media/Disney logo_White.png" alt="Disney Logo" className="logo-disney" />
          </div>
        </div>
      </header>
      <main className="main">
        <div className="left-panel">
          {/* 标签页头部 */}
          <div className="tab-headers">
            <button 
              className={`tab ${activeTab === "TRAVEL GUIDE" ? "active" : ""}`}
              onClick={() => setActiveTab("TRAVEL GUIDE")}
            >
              TRAVEL GUIDE
            </button>
            <button 
              className={`tab ${activeTab === "Q&A" ? "active" : ""}`}
              onClick={() => setActiveTab("Q&A")}
            >
              Q&A
            </button>
            <button 
              className={`tab ${activeTab === "CHAT" ? "active" : ""}`}
              onClick={() => setActiveTab("CHAT")}
            >
              CHAT
            </button>
          </div>

          <div className="tab-content">
            {activeTab === "TRAVEL GUIDE" && (
              <>
                <div className="input-guide">
                  <div className="input-guide-content">
                    <div className="preview-content">
                      {isLoading ? (
                        <div className="loading-indicator">
                          Planning...
                        </div>
                      ) : guide ? (
                        <div 
                          className="markdown-content"
                          dangerouslySetInnerHTML={{ 
                            __html: typeof guide === 'string' ? marked.parse(guide) : guide 
                          }}
                        />
                      ) : (
                        <>
                          <h1>Plan your perfect Disney adventure! 🎢✨</h1>
                          <p>Welcome to Magic Trail, your personal Disney itinerary planner!</p>
                          <h2>What We Offer</h2>
                          <p>
                            Magic Trail is designed to create the perfect Disney experience tailored just for you. Our AI-powered system takes into account your:
                          </p>
                          <ul>
                            <li>Preferred attractions</li>
                            <li>Available time</li>
                            <li>Group composition</li>
                          </ul>
                          <span>...
                            <span 
                              className="read-more-link" 
                              onClick={() => setShowModal(true)}
                            >
                              read more
                            </span>
                          </span>
                        </>
                      )}
                    </div>
                  </div>
                </div>
                <form onSubmit={handleSubmit} method="POST">
                  <button
                    type="button"
                    className="requirements-btn"
                    onClick={() => setShowRequirementsModal(true)}
                  >
                    Plan My Trip
                  </button>
                </form>
              </>
            )}

            {activeTab === "Q&A" && (
              <div className="coming-soon">
                Coming Soon
              </div>
            )}

            {activeTab === "CHAT" && (
              <div className="input-guide">
                {isLoading ? '正在思考中...' : guide}
              </div>
            )}
          </div>
        </div>
        <div id="map-container" className="map-container"></div>
      </main>
      
      {showModal && (
        <div className="modal-overlay">
          <div className="modal-content" onClick={e => e.stopPropagation()}>
            <div className="modal-header">
              <h2>Magic Trail Guide</h2>
              <button className="modal-close" onClick={() => setShowModal(false)}>×</button>
            </div>
            <div 
              className="blog-content"
              dangerouslySetInnerHTML={{ __html: marked(blogContent) }}
            />
          </div>
        </div>
      )}

      {showRequirementsModal && (
        <div className="modal-overlay">
          <div className="modal-content requirements-modal">
            <div className="modal-header">
              <h2>Plan My Trip</h2>
              <button 
                className="modal-close" 
                onClick={() => setShowRequirementsModal(false)}
              >
                ×
              </button>
            </div>
            
            <div className="modal-body requirements-form">
              <div className="form-group">
                <label>性别</label>
                <select name="gender" value={formData.gender} onChange={handleInputChange}>
                  <option value="female">女</option>
                  <option value="male">男</option>
                </select>
              </div>

              <div className="form-group">
                <label>年龄</label>
                <input
                  type="number"
                  name="age"
                  value={formData.age}
                  onChange={handleInputChange}
                />
              </div>

              <div className="form-group">
                <label>生日</label>
                <input
                  type="date"
                  name="birthday"
                  value={formData.birthday}
                  onChange={handleInputChange}
                />
              </div>

              <div className="form-group">
                <label>同行人数</label>
                <input
                  type="number"
                  name="groupSize"
                  value={formData.groupSize}
                  onChange={handleInputChange}
                />
              </div>

              <div className="form-group">
                <label>同行人身份</label>
                <select 
                  name="companions" 
                  value={formData.companions[0] || ''} 
                  onChange={handleInputChange}
                  multiple={false}
                >
                  <option value="">请选择</option>
                  <option value="闺蜜">闺蜜</option>
                  <option value="情侣">情侣</option>
                  <option value="朋友">朋友</option>
                  <option value="家庭">家庭</option>
                </select>
              </div>

              <div className="form-group">
                <label>是否携带儿童</label>
                <select name="hasChildren" value={formData.hasChildren} onChange={handleInputChange}>
                  <option value="否">否</option>
                  <option value="是">是</option>
                </select>
              </div>

              {formData.hasChildren === '是' && (
                <>
                  <div className="form-group">
                    <label>儿童年龄</label>
                    <input
                      type="number"
                      name="childAge"
                      value={formData.childAge}
                      onChange={handleInputChange}
                    />
                  </div>

                  <div className="form-group">
                    <label>儿童身高(cm)：</label>
                    <input
                      type="number"
                      name="childHeight"
                      value={formData.childHeight}
                      onChange={handleInputChange}
                    />
                  </div>
                </>
              )}

              <div className="form-group">
                <label>是否有就餐需要</label>
                <select name="needsDining" value={formData.needsDining} onChange={handleInputChange}>
                  <option value="否">否</option>
                  <option value="是">是</option>
                </select>
              </div>

              <div className="form-group">
                <label>预计游玩时长</label>
                <input
                  type="text"
                  name="visitTime"
                  value={formData.visitTime}
                  placeholder="例如：9:00-18:00"
                  onChange={handleInputChange}
                />
              </div>

              <div className="form-group">
                <label>是否首次入园</label>
                <select name="firstVisit" value={formData.firstVisit} onChange={handleInputChange}>
                  <option value="是">是</option>
                  <option value="否">否</option>
                </select>
              </div>

              <div className="form-group">
                <label>是否特殊日期入园</label>
                <select name="specialDate" value={formData.specialDate} onChange={handleInputChange}>
                  <option value="">无</option>
                  <option value="生日">生日</option>
                  <option value="纪念日">纪念日</option>
                </select>
              </div>

              <div className="form-group">
                <label>游玩偏好</label>
                <select name="preference" value={formData.preference} onChange={handleInputChange}>
                  <option value="无特殊偏好">无特殊偏好</option>
                  <option value="迪士尼特种兵">迪士尼特种兵</option>
                  <option value="打卡新鲜事">打卡新鲜事</option>
                  <option value="超悠闲逛吃">超悠闲逛吃</option>
                  <option value="乐拍一整天">乐拍一整天</option>
                </select>
              </div>

              <div className="form-group">
                <label>迪士尼人物偏好</label>
                <input
                  type="text"
                  name="characterPreference"
                  value={formData.characterPreference}
                  onChange={handleInputChange}
                  placeholder="例如：米老鼠、唐老鸭"
                />
              </div>

              <div className="form-group">
                <label>门票类型</label>
                <select name="ticketType" value={formData.ticketType} onChange={handleInputChange}>
                  <option value="标准票">标准票</option>
                  <option value="儿童票">儿童票</option>
                  <option value="老年人票">老年人票</option>
                  <option value="残障人士票">残障人士票</option>
                </select>
              </div>

              <div className="form-group">
                <label>其它备注</label>
                <textarea
                  name="additionalNotes"
                  value={formData.additionalNotes}
                  onChange={handleInputChange}
                  placeholder="请输入其它需求或备注..."
                />
              </div>

              <div className="modal-footer">
                <button 
                  type="button" 
                  className="modal-cancel-btn"
                  onClick={() => setShowRequirementsModal(false)}
                >
                  Cancel
                </button>
                <button 
                  type="button" 
                  className="modal-submit-btn"
                  onClick={handleSubmit}
                >
                  Generate
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default App;