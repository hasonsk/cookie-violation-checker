import Sidebar from '../components/Sidebar';
import Topbar from '../components/topbars/TopBar';
import { Outlet } from 'react-router-dom';
import Footer from '../components/footer/Footer'

export default function AdminLayout() {
  return (
    <div className="flex bg-gray-50 min-h-screen" style={{ marginLeft: '300px' }}>
      <Sidebar />
      <div className="flex-1">
        <Topbar />
        <main className="p-6">
          <Outlet />
          <Footer />
        </main>
      </div>
    </div>
  );
}
