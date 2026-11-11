package app.suasflux.modulo.config;


import java.util.Objects;

import javax.sql.DataSource;

import org.flywaydb.core.Flyway;
import org.springframework.beans.factory.annotation.Qualifier;
import org.springframework.boot.context.properties.ConfigurationProperties;
import org.springframework.boot.jdbc.autoconfigure.DataSourceProperties;
import org.springframework.boot.jpa.EntityManagerFactoryBuilder;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.context.annotation.DependsOn;
import org.springframework.data.jpa.repository.config.EnableJpaRepositories;
import org.springframework.orm.jpa.JpaTransactionManager;
import org.springframework.orm.jpa.LocalContainerEntityManagerFactoryBean;
import org.springframework.transaction.PlatformTransactionManager;
import org.springframework.transaction.annotation.EnableTransactionManagement;

@Configuration
@EnableTransactionManagement
@EnableJpaRepositories(
        basePackages = "app.suasflux.modulo.federacao",
        entityManagerFactoryRef = "federacaoEntityManagerFactory",
        transactionManagerRef = "federacaoTransactionManager"
)
public class FederacaoDbConfig {
	
	
    @Bean
    @ConfigurationProperties("app.datasource.federacao")
    public DataSourceProperties federacaoDataSourceProperties() {
        return new DataSourceProperties();
    }
	
	
    @Bean
    public DataSource federacaoDataSource(
            @Qualifier("federacaoDataSourceProperties") DataSourceProperties properties) {
        return properties.initializeDataSourceBuilder().build();
    }
	
	
    @Bean
    public Flyway federacaoFlyway(
            @Qualifier("federacaoDataSource") DataSource dataSource) {
        return Flyway.configure()
                .dataSource(dataSource)
                .locations(
                    "classpath:db/setupschema/federacao",
                    "classpath:db/migration/federacao",
                    "classpath:db/legacydata/federacao"
                )
                .baselineOnMigrate(true)  // Útil para DBs existentes
                .load();
    }
	
	
    @Bean
    @DependsOn("federacaoFlyway")  // Garante ordem sem injeção fantasma
    public LocalContainerEntityManagerFactoryBean federacaoEntityManagerFactory(
            EntityManagerFactoryBuilder builder,
            @Qualifier("federacaoDataSource") DataSource dataSource) {
        
        return builder
                .dataSource(dataSource)
                .packages("app.suasflux.modulo.federacao")
                .persistenceUnit("federacao")
                .build();
    }
	

    @Bean
    public PlatformTransactionManager federacaoTransactionManager(
            @Qualifier("federacaoEntityManagerFactory") 
            LocalContainerEntityManagerFactoryBean entityManagerFactory) {
        
        return new JpaTransactionManager(
            Objects.requireNonNull(entityManagerFactory.getObject(), 
                "EntityManagerFactory não inicializada")
        );
    }
}
