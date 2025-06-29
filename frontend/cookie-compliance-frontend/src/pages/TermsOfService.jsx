import React from 'react';
import { Box, Typography, Container, Link } from '@mui/material';
import { Link as RouterLink } from 'react-router-dom';

const TermsOfService = () => {
  return (
    <Container maxWidth="md" sx={{ mt: 4, mb: 4 }}>
      <Box sx={{ my: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          Điều khoản sử dụng
        </Typography>
        <Typography variant="body1" paragraph>
          Chào mừng bạn đến với Cookie Compliance Checker. Bằng cách truy cập hoặc sử dụng dịch vụ của chúng tôi, bạn đồng ý tuân thủ các điều khoản và điều kiện sau đây. Vui lòng đọc kỹ trước khi sử dụng dịch vụ.
        </Typography>

        <Typography variant="h5" component="h2" gutterBottom sx={{ mt: 3 }}>
          1. Chấp nhận Điều khoản
        </Typography>
        <Typography variant="body1" paragraph>
          Bằng việc sử dụng dịch vụ của chúng tôi, bạn xác nhận rằng bạn đã đọc, hiểu và đồng ý bị ràng buộc bởi các Điều khoản sử dụng này. Nếu bạn không đồng ý với bất kỳ điều khoản nào, vui lòng không sử dụng dịch vụ của chúng tôi.
        </Typography>

        <Typography variant="h5" component="h2" gutterBottom sx={{ mt: 3 }}>
          2. Thay đổi Điều khoản
        </Typography>
        <Typography variant="body1" paragraph>
          Chúng tôi có quyền sửa đổi các Điều khoản sử dụng này bất cứ lúc nào. Mọi thay đổi sẽ có hiệu lực ngay khi được đăng tải trên trang web của chúng tôi. Việc bạn tiếp tục sử dụng dịch vụ sau khi các thay đổi được đăng tải đồng nghĩa với việc bạn chấp nhận các điều khoản đã sửa đổi.
        </Typography>

        <Typography variant="h5" component="h2" gutterBottom sx={{ mt: 3 }}>
          3. Quyền riêng tư
        </Typography>
        <Typography variant="body1" paragraph>
          Chính sách bảo mật của chúng tôi giải thích cách chúng tôi thu thập, sử dụng và bảo vệ thông tin cá nhân của bạn. Bằng cách sử dụng dịch vụ của chúng tôi, bạn đồng ý với việc thu thập và sử dụng thông tin của bạn theo Chính sách bảo mật của chúng tôi. Bạn có thể xem Chính sách bảo mật tại đây:{' '}
          <Link component={RouterLink} to="/privacy-policy" sx={{ color: 'primary.main', textDecoration: 'none', '&:hover': { textDecoration: 'underline' } }}>
            Chính sách bảo mật
          </Link>.
        </Typography>

        <Typography variant="h5" component="h2" gutterBottom sx={{ mt: 3 }}>
          4. Hành vi người dùng
        </Typography>
        <Typography variant="body1" paragraph>
          Bạn đồng ý không sử dụng dịch vụ của chúng tôi cho bất kỳ mục đích bất hợp pháp hoặc bị cấm bởi các Điều khoản này. Bạn không được:
          <ul>
            <li>Vi phạm bất kỳ luật pháp hoặc quy định hiện hành nào.</li>
            <li>Gửi hoặc truyền tải bất kỳ nội dung nào là bất hợp pháp, có hại, đe dọa, lạm dụng, quấy rối, phỉ báng, tục tĩu, khiêu dâm, bôi nhọ, xâm phạm quyền riêng tư của người khác, hoặc gây khó chịu về chủng tộc, dân tộc hoặc các vấn đề khác.</li>
            <li>Cố gắng truy cập trái phép vào hệ thống máy tính hoặc mạng lưới của chúng tôi.</li>
            <li>Can thiệp hoặc làm gián đoạn dịch vụ hoặc các máy chủ hoặc mạng được kết nối với dịch vụ.</li>
          </ul>
        </Typography>

        <Typography variant="h5" component="h2" gutterBottom sx={{ mt: 3 }}>
          5. Giới hạn trách nhiệm
        </Typography>
        <Typography variant="body1" paragraph>
          Dịch vụ của chúng tôi được cung cấp "nguyên trạng" và "như có sẵn" mà không có bất kỳ bảo đảm nào, dù rõ ràng hay ngụ ý. Chúng tôi không đảm bảo rằng dịch vụ sẽ không bị gián đoạn, không có lỗi hoặc an toàn. Trong mọi trường hợp, chúng tôi sẽ không chịu trách nhiệm về bất kỳ thiệt hại trực tiếp, gián tiếp, ngẫu nhiên, đặc biệt hoặc do hậu quả nào phát sinh từ việc sử dụng hoặc không thể sử dụng dịch vụ của chúng tôi.
        </Typography>

        <Typography variant="h5" component="h2" gutterBottom sx={{ mt: 3 }}>
          6. Bồi thường
        </Typography>
        <Typography variant="body1" paragraph>
          Bạn đồng ý bồi thường và giữ cho chúng tôi vô hại khỏi mọi khiếu nại, thiệt hại, nghĩa vụ, tổn thất, chi phí hoặc nợ phát sinh từ việc bạn sử dụng dịch vụ hoặc vi phạm các Điều khoản này.
        </Typography>

        <Typography variant="h5" component="h2" gutterBottom sx={{ mt: 3 }}>
          7. Luật điều chỉnh
        </Typography>
        <Typography variant="body1" paragraph>
          Các Điều khoản sử dụng này sẽ được điều chỉnh và giải thích theo luật pháp Việt Nam, không tính đến các xung đột về nguyên tắc pháp luật.
        </Typography>

        <Typography variant="h5" component="h2" gutterBottom sx={{ mt: 3 }}>
          8. Liên hệ
        </Typography>
        <Typography variant="body1" paragraph>
          Nếu bạn có bất kỳ câu hỏi nào về các Điều khoản sử dụng này, vui lòng liên hệ với chúng tôi qua email: support@cookiecompliance.com.
        </Typography>
      </Box>
    </Container>
  );
};

export default TermsOfService;
