import Container from 'react-bootstrap/Container';
import Nav from 'react-bootstrap/Nav';
import Navbar from 'react-bootstrap/Navbar';
import NavDropdown from 'react-bootstrap/NavDropdown';

function NavTop() {
  return (
    <Navbar
      expand="lg"
      className="fixed-top"
      style={{ backgroundColor: '#932d2d', color: 'white' }}
    >
      <Container>
        <Navbar.Brand href="#home" style={{ color: 'white' }}>
          React-Bootstrap
        </Navbar.Brand>
        <Navbar.Toggle aria-controls="basic-navbar-nav" />
        <Navbar.Collapse id="basic-navbar-nav">
          <Nav className="me-auto">
            <Nav.Link href="/" style={{ color: 'white' }}>
              Home
            </Nav.Link>
            <Nav.Link href="/filter" style={{ color: 'white' }}>
              Data Filtration
            </Nav.Link>
            <NavDropdown
              title="Sign up + Login"
              id="basic-nav-dropdown"
              style={{ color: 'white' }}
              // Inline styles using popperConfig to style the dropdown menu container
              popperConfig={{
                modifiers: [
                  {
                    name: 'styles',
                    options: {
                      styles: {
                        popper: {
                          backgroundColor: '#932d2d', // Red background for dropdown menu
                          color: 'white',             // Default text color in dropdown (if needed)
                          border: '1px solid white',   // Example: White border for rounded edges
                          borderRadius: '0.25rem',    // Keep default border-radius or adjust
                          // You can add more styles here to control the dropdown menu container
                        },
                      },
                    },
                  },
                ],
              }}
            >
              <NavDropdown.Item href="/hlogin" style={{ color: 'white', backgroundColor: '#932d2d' }} >Hospital Login</NavDropdown.Item>
              <NavDropdown.Item href="/hsign" style={{ color: 'white', backgroundColor: '#932d2d' }}>
                Hospital Sign Up
              </NavDropdown.Item>
              <NavDropdown.Item href="/dsign" style={{ color: 'white', backgroundColor: '#932d2d' }}>Donor Sign Up</NavDropdown.Item>
            </NavDropdown>
          </Nav>
        </Navbar.Collapse>
      </Container>
    </Navbar>
  );
}

export default NavTop;