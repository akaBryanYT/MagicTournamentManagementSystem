import React from 'react';
import { Container } from 'react-bootstrap';

const Footer: React.FC = () => {
  return (
    <footer className="bg-dark text-white py-3 mt-auto">
      <Container className="text-center">
        <p className="mb-0">Tournament Management System &copy; {new Date().getFullYear()}</p>
        <p className="small mb-0">A comprehensive solution for Magic: The Gathering tournaments</p>
      </Container>
    </footer>
  );
};

export default Footer;
