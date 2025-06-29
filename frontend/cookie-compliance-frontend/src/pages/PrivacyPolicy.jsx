import React from 'react';
import { Box, Typography, Container, Link } from '@mui/material';
import { Link as RouterLink } from 'react-router-dom';

const PrivacyPolicy = () => {
  return (
    <Container maxWidth="md" sx={{ mt: 4, mb: 4 }}>
      <Box sx={{ my: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          Chính sách bảo mật
        </Typography>
        <Typography variant="body1" paragraph>
          Tại Cookie Compliance Checker, chúng tôi cam kết bảo vệ quyền riêng tư của bạn. Chính sách bảo mật này giải thích cách chúng tôi thu thập, sử dụng, tiết lộ và bảo vệ thông tin của bạn khi bạn sử dụng dịch vụ của chúng tôi.
        </Typography>

        <Typography variant="h5" component="h2" gutterBottom sx={{ mt: 3 }}>
          1. Thông tin chúng tôi thu thập
        </Typography>
        <Typography variant="body1" paragraph>
          Chúng tôi có thể thu thập các loại thông tin sau:
          <ul>
            <li>Thông tin cá nhân: Tên, địa chỉ email, thông tin liên hệ khác mà bạn cung cấp khi đăng ký hoặc sử dụng dịch vụ của chúng tôi.</li>
            <li>Thông tin sử dụng: Dữ liệu về cách bạn tương tác với dịch vụ của chúng tôi, bao gồm địa chỉ IP, loại trình duyệt, trang đã truy cập, thời gian truy cập và các số liệu thống kê khác.</li>
            <li>Thông tin cookie: Chúng tôi sử dụng cookie và các công nghệ theo dõi tương tự để theo dõi hoạt động trên dịch vụ của chúng tôi và lưu giữ một số thông tin nhất định.</li>
          </ul>
        </Typography>

        <Typography variant="h5" component="h2" gutterBottom sx={{ mt: 3 }}>
          2. Cách chúng tôi sử dụng thông tin của bạn
        </Typography>
        <Typography variant="body1" paragraph>
          Chúng tôi sử dụng thông tin thu thập được cho các mục đích sau:
          <ul>
            <li>Cung cấp và duy trì dịch vụ của chúng tôi.</li>
            <li>Cải thiện, cá nhân hóa và mở rộng dịch vụ của chúng tôi.</li>
            <li>Phân tích cách bạn sử dụng dịch vụ của chúng tôi.</li>
            <li>Phát hiện, ngăn chặn và giải quyết các vấn đề kỹ thuật.</li>
            <li>Liên hệ với bạn để cung cấp thông tin cập nhật, thông báo và các thông tin liên quan đến dịch vụ.</li>
          </ul>
        </Typography>

        <Typography variant="h5" component="h2" gutterBottom sx={{ mt: 3 }}>
          3. Chia sẻ thông tin của bạn
        </Typography>
        <Typography variant="body1" paragraph>
          Chúng tôi không bán, trao đổi hoặc cho thuê thông tin cá nhân của bạn cho bên thứ ba. Chúng tôi có thể chia sẻ thông tin của bạn với các nhà cung cấp dịch vụ bên thứ ba đáng tin cậy để hỗ trợ chúng tôi vận hành trang web, tiến hành hoạt động kinh doanh hoặc phục vụ bạn, miễn là các bên đó đồng ý giữ bí mật thông tin này. Chúng tôi cũng có thể tiết lộ thông tin của bạn khi chúng tôi tin rằng việc tiết lộ là phù hợp để tuân thủ luật pháp, thực thi các chính sách của trang web hoặc bảo vệ quyền, tài sản hoặc sự an toàn của chúng tôi hoặc của người khác.
        </Typography>

        <Typography variant="h5" component="h2" gutterBottom sx={{ mt: 3 }}>
          4. Bảo mật dữ liệu
        </Typography>
        <Typography variant="body1" paragraph>
          Chúng tôi áp dụng các biện pháp bảo mật hợp lý để bảo vệ thông tin cá nhân của bạn khỏi việc truy cập, sử dụng hoặc tiết lộ trái phép. Tuy nhiên, không có phương pháp truyền tải qua Internet hoặc phương pháp lưu trữ điện tử nào là an toàn 100%. Do đó, chúng tôi không thể đảm bảo an ninh tuyệt đối cho thông tin của bạn.
        </Typography>

        <Typography variant="h5" component="h2" gutterBottom sx={{ mt: 3 }}>
          5. Quyền của bạn
        </Typography>
        <Typography variant="body1" paragraph>
          Bạn có quyền truy cập, cập nhật hoặc xóa thông tin cá nhân của mình. Nếu bạn muốn thực hiện các quyền này, vui lòng liên hệ với chúng tôi.
        </Typography>

        <Typography variant="h5" component="h2" gutterBottom sx={{ mt: 3 }}>
          6. Liên kết đến các trang web khác
        </Typography>
        <Typography variant="body1" paragraph>
          Dịch vụ của chúng tôi có thể chứa các liên kết đến các trang web khác không do chúng tôi điều hành. Nếu bạn nhấp vào liên kết của bên thứ ba, bạn sẽ được chuyển hướng đến trang web của bên thứ ba đó. Chúng tôi khuyên bạn nên xem lại Chính sách bảo mật của mọi trang web bạn truy cập. Chúng tôi không kiểm soát và không chịu trách nhiệm về nội dung, chính sách bảo mật hoặc thực tiễn của bất kỳ trang web hoặc dịch vụ bên thứ ba nào.
        </Typography>

        <Typography variant="h5" component="h2" gutterBottom sx={{ mt: 3 }}>
          7. Thay đổi Chính sách bảo mật này
        </Typography>
        <Typography variant="body1" paragraph>
          Chúng tôi có thể cập nhật Chính sách bảo mật của mình theo thời gian. Chúng tôi sẽ thông báo cho bạn về bất kỳ thay đổi nào bằng cách đăng Chính sách bảo mật mới trên trang này. Bạn nên xem lại Chính sách bảo mật này định kỳ để biết bất kỳ thay đổi nào.
        </Typography>

        <Typography variant="h5" component="h2" gutterBottom sx={{ mt: 3 }}>
          8. Liên hệ
        </Typography>
        <Typography variant="body1" paragraph>
          Nếu bạn có bất kỳ câu hỏi nào về Chính sách bảo mật này, vui lòng liên hệ với chúng tôi qua email: support@cookiecompliance.com.
        </Typography>
      </Box>
    </Container>
  );
};

export default PrivacyPolicy;
